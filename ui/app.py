import base64
import streamlit as st
from PIL import Image
import requests
import io

# Page Title
st.title("ImageWithin: Search for an image in another image :sparkles:", )
# Layout
st.write("Upload your images below:")

# Drop zones for image uploads
col1, col2 = st.columns(2)

with col1:
    actual_image = st.file_uploader("Upload the Actual Image", type=["png", "jpg", "jpeg"])
    if not actual_image:
        st.warning("Please upload the actual image before submitting.")
    # Check if the size exceeds 5MB
    if actual_image and actual_image.size > 5 * 1024 * 1024:
        st.error("Please upload an image smaller than 2MB and retry")
        st.stop()
    if actual_image:
        actual_img = Image.open(actual_image)
        st.image(actual_img, caption="Actual Image", use_container_width=True)

with col2:
    search_image = st.file_uploader("Upload the Reference/Search Image", type=["png", "jpg", "jpeg"])
    if not search_image:
        st.warning("Please upload the reference/search image before submitting.")
    # Check if the size exceeds 2MB
    if search_image and search_image.size > 5 * 1024 * 1024:
        st.error("Please upload an image smaller than 2MB.")
        st.write("Click the button below to refresh the page.")
        if st.button("Refresh Page"):    
            refresh_page()  # Call JavaScript refresh
        st.stop()
    if search_image:
        search_img = Image.open(search_image)
        st.image(search_img, caption="Reference/Search Image", use_container_width=True)

# Submit button
if st.button("Submit"):
    # Check if both images are uploaded
    if actual_image and search_image:
        # Send images to backend API
        st.write("Processing images... Please wait.")
        
        # Mock API Endpoint
        api_url = "http://localhost:8000/api/v1/imagewithin"

        # Prepare the Form with image and index
        payload = {
            "index": 1,
            "baseImageName": str(actual_image.name),
            "refImageName": str(search_image.name)
        }

        inputfiles = [
            ("baseImage", actual_image.getvalue()),
            ("refImage", search_image.getvalue()),
        ]
        
        try:
            # Send POST request to backend
            response = requests.post(api_url, data=payload, files=inputfiles)
            # Check if the response is successful
            if response.status_code == 200:
                print("API Response:", response)
                # Parse response
                # If the response content type is JSON then display the response
                if response.headers.get("Content-Type") == "application/json":
                    response_data = response.json()
                    st.error("Sorry!. we could not find the reference image in the actual image.\n this is our API response")
                    st.json(response_data)
                # If the response content type is image then display the image
                elif response.headers.get("Content-Type") == "image/png":
                    # Show the content-type image
                    st.success("Successfully identified the reference image in the actual image.\n we marked the location of the reference image on the actual image.")
                    st.image(response.content,  use_container_width=True)
                else:
                    st.error("Unknown response content type: " + response.headers.get("Content-Type"))
                    st.write(response.text)
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            st.error(f"Error connecting to API: {e}")
    else:
        st.warning("Please upload both images before submitting.")
