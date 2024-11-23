__package__ = "controller"

import gzip
import cv2
import numpy as np
import os
from loguru import logger 
import sys
import base64
from common import FindCoordsSchema, imageControllerSchema, imageControllerError, imageControllerSuccess
from fastapi.responses import FileResponse


class ImageController:
    
    def __init__(self, imgctrl: imageControllerSchema) -> None:
        """
        Initialize ImageController with the given base image, reference image, and request ID.
        """
        
        self.baseimage = imgctrl.baseImage
        self.refimage = imgctrl.refImage
        self.reqid = imgctrl.req_id
        self.index = imgctrl.index
        self.x = imgctrl.x
        self.y = imgctrl.y
        self.matchtemplate_result = {}
        self.accuracy = 0

        # Add logger with format that includes request_id
        logger.remove()  # Remove the default handler to avoid duplicate logs
        logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | <level>{level}</level> | {function} | req={extra[request_id]} | {message} ", level="INFO")
        self.log = logger.bind(request_id=imgctrl.req_id)  # Bind the request_id to logger
    
      
    def matchTemplate(self):
        #Check the provided baseimage and ref image path
        if not os.path.exists(self.baseimage) and not os.path.exists(self.refimage):
            self.log.info(f"Images not found on the local filesystem")

            self.matchtemplate_result = imageControllerError(
                message="Images not found on the local filesystem"
            )
            return self.matchtemplate_result

        # Load the image
        image = cv2.imread(self.baseimage)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply threshold or edge detection
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # Load the template of the ref image
        refImg = cv2.imread(self.refimage, 0)

        # Perform template matching
        result = cv2.matchTemplate(gray, refImg, cv2.TM_CCOEFF_NORMED)

        threshold = os.getenv("IMG_MATCH_THRESHOLD", 0.9)
        locations = np.where(result >= float(threshold))

        # if the location is not found
        if not locations[0].any() and not locations[1].any():
            self.matchtemplate_result = imageControllerError(
                message="No matches found"
            )
            return self.matchtemplate_result
        
        # Store the matched locations
        matches = []

        # Why we need to reverse the order?
        # Because we need to get x, y coordinates in the right-to-left order
        # for the template matching algorithm to work.
        for loc in zip(*locations[::-1]):  # Reverse to get x, y coordinates
            matches.append(loc)

        # Sort matches by x-coordinate (left to right)
        sorted_matches = sorted(matches, key=lambda x: x[0])  # Sort by the x-coordinate (left-right order)

        # Print the coordinates of all the matched elements
        for idx, match in enumerate(sorted_matches):
            print(f"Button {idx}: Coordinates (x={match[0]}, y={match[1]})")

        self.matchtemplate_result = imageControllerSuccess(
            matches=sorted_matches,
            result=result,
            image=image,
            refImg=refImg
        )

        # self.matchtemplate_result = {
        #     "status": "success",
        #     "matches": sorted_matches,
        #     "result": result,
        #     "image": image,
        #     "refImg": refImg
        # }


    def matchTemplateScaled(self):
        # Check if either the baseimage or ref image paths are missing
        if not os.path.exists(self.baseimage) or not os.path.exists(self.refimage):
            self.log.info("Images not found on the local filesystem")
            self.matchtemplate_result = imageControllerError(
                message="Images not found on the local filesystem"
            )
            return self.matchtemplate_result

        # Load the images
        image = cv2.imread(self.baseimage)

        # the 0 flag indicates that the image is loaded in grayscale
        refImg = cv2.imread(self.refimage, 0)

        # Scaling factors
        scales = [2.0,1.0,0.9,0.7,0.8,0.6,0.5,0.2]
        threshold = float(os.getenv("IMG_MATCH_THRESHOLD", 0.9))
        found_matches = False  # To track if we find any match

        # Convert the base image to grayscale
        graybaseImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # save the image and ref image
        cv2.imwrite(self.reqid+"_"+self.baseimage, image)
        cv2.imwrite(self.reqid+"_"+self.refimage, refImg)
    
        for scale in scales:

            self.log.info("Checking scale: {scale}".format(scale=scale))
            scaled_refImg = cv2.resize(refImg, None, fx=scale, fy=scale)
            
            # Ensure the scaled refImage is smaller than the base image
            if scaled_refImg.shape[0] > graybaseImage.shape[0] or scaled_refImg.shape[1] > graybaseImage.shape[1]:
                self.log.info("Scaled refImage is larger than the base image{0}".format(scaled_refImg.shape))
                continue

            scaled_result = cv2.matchTemplate(graybaseImage, scaled_refImg, cv2.TM_CCOEFF_NORMED)

            # Save the scaled images
            scaledRefImagePath = os.path.join("images", self.reqid, "scaled-{scale}-elementimage.png".format(scale=scale))
            cv2.imwrite(scaledRefImagePath, scaled_refImg)

            # Find locations above the threshold
            locations = np.where(scaled_result >= threshold)
            matches = [loc for loc in zip(*locations[::-1])]  # Get x, y coordinates

            self.log.info(f"Found {len(matches)} matches at scale {scale}") if matches else ""

            # If we found matches, log them and exit the loop
            if matches:
                found_matches = True
                sorted_matches = sorted(matches, key=lambda x: x[0])  # Sort by x-coordinate

                # if more than 5 matches, take only the first 5
                if len(sorted_matches) > 5:
                    sorted_matches = sorted_matches[:5]

                for idx, match in enumerate(sorted_matches):
                    self.log.info(f"Button {idx}: Coordinates (x={match[0]}, y={match[1]})")

                self.matchtemplate_result = imageControllerSuccess(
                    matches=sorted_matches,
                    result=scaled_result,
                    image=image,
                    refImg=refImg
                )
                # self.matchtemplate_result = {
                #     "status": "success",
                #     "matches": sorted_matches,
                #     "result": scaled_result,
                #     "image": image,
                #     "refImg": refImg
                # }
                break  # Exit the loop once matches are found

        # If no matches found after all scales, set result to error
        if not found_matches:
            self.log.error("No matches found")
            self.matchtemplate_result = imageControllerError(
                message="No matches found"
            )


    def find_x_y(self):

        # Call the matchTemplate function
        self.matchTemplate()

        # Validate the response
        if self.matchtemplate_result and self.matchtemplate_result.status == "error":
            if self.matchtemplate_result.message == "No matches found":
                self.log.info("No matching element found with original image, trying to match with scaled images")
                # Call the matchTemplateScaled function
                self.matchTemplateScaled()
                # Validate the response once again
                if self.matchtemplate_result and self.matchtemplate_result.status == "error":
                    return self.matchtemplate_result
        
        
        image = self.matchtemplate_result.image
        result = self.matchtemplate_result.result
        sorted_matches = self.matchtemplate_result.matches
        refImg = self.matchtemplate_result.refImg

        # Find the Index based on input
        if self.index >= len(sorted_matches):
            print("Matching element found but Index out of range")
            return {"message": "Matching element found but Index out of range"}
        else:
            print(f"element {self.index} is at: (x={sorted_matches[self.index][0]}, y={sorted_matches[self.index][1]})")

        # get the minmaxloc of self.index matched element
        element_x, element_y = sorted_matches[self.index]

        # return the accuracy of the self.index matched element
        accuracy = result[element_y, element_x] * 100
        
        # Highlight the matched area
        h, w = refImg.shape

        cv2.rectangle(image, (element_x, element_y), (element_x + w, element_y + h), (0, 255, 0), 2)

        # save the image to local
        output_dir = os.path.join("images", self.reqid)
        cv2.imwrite(output_dir + "/output.png", image)

        # Print the values before returning them
        self.log.info(f" Accuracy: {accuracy:.5f}% " + f"element coordinates: ({element_x}, {element_y})")

        #  Return image
        return FileResponse(output_dir + "/output.png")
        
        
        