import fastapi
from dotenv import load_dotenv
from pydantic import BaseModel
import requests
import uvicorn
from utils import validators
from controller import imagecontroller
import uuid
from loguru import logger as log
from common import FindCoordsSchema, imageControllerSchema, find_coords_schema
import os
load_dotenv()
import pdb


app = fastapi.FastAPI()

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.post("/api/v1/imagewithin")
async def find_image_within(images: FindCoordsSchema = fastapi.Depends(find_coords_schema)):
    # Create a Unique Request ID to track the request
    req_id = str(uuid.uuid4())

    # Download the images to local storage from multipart request
    baseImagePath = os.path.join("images", str(req_id), "baseimage" + "." + images.baseImageName.split(".")[-1]) 
    referenceImagePath = os.path.join("images", str(req_id), "referenceimage" + "." + images.refImageName.split(".")[-1])

    log.info(f"Starting ImageWithin Request: {req_id}, baseImage: {baseImagePath}, refImage: {referenceImagePath}, baseImageName: {images.baseImageName}, refImageName: {images.refImageName}, index: {images.index}") # Log Request with inputs

    uploads_dir = os.path.join("images", str(req_id))
    os.makedirs(uploads_dir, exist_ok=True)

    with open(baseImagePath, "wb") as f:
        f.write(images.baseImage.file.read())
    with open(referenceImagePath, "wb") as f:
        f.write(images.refImage.file.read())

    #Find the coordinates
    idx = images.index - 1 # Converting user input to 0 based index

    findxy_schema = imageControllerSchema(baseImage=baseImagePath, refImage=referenceImagePath, index=idx, x=0, y=0, req_id=req_id)
    imctrl =  imagecontroller.ImageController(findxy_schema)
    
    return imctrl.find_x_y()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)