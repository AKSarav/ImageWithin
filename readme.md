# Image Within - Find Images Within Another Image :sparkles:

An Experiment Project with API and Web Interface created to Find Images Within Another Image

The Following technologies are used in this project
- openCV
- numpy
- fastapi
- streamlit

This is the UI - where you can upload your images
![UI](assets/ImageWithinUI.png)

This is the Result - You can see the output highlighted in green annotation - Rectangle
![Result](assets/ImageWithinResult.png)



&nbsp;

## The Logic behind

The logical comparision is now powered by OpenCV's `matchTemplate` and `cv2.TM_CCOEFF_NORMED`

I am currently working on AI Custom Models to improve the accuracy of the results and to enhance the scope of the project

Here are some modeles I am trying right now

- Yolov8
- CNN Model
- OpenCV DNN Model https://docs.opencv.org/4.x/d2/d58/tutorial_table_of_content_dnn.html

```
cv2.matchTemplate(graybaseImage, scaled_refImg, cv2.TM_CCOEFF_NORMED)
```

> This is an experiment project created to Find Images Within Another Image and to test the performance of OpenCV's `matchTemplate` and `cv2.TM_CCOEFF_NORMED` and other algorithms and provide an interface for future AI - ML based model validations - Feel free to contribute

&nbsp;

## How to use it

1. Download the project
``` 
git clone https://github.com/robertoferreira/image-within.git 
```

2. Install the requirements
``` 
pip install -r requirements.txt 
```

3. Run the UI
```
streamlit run ui/app.py 
```

4. Run the API
```
cd api && uvicorn app:app --reload
```

5. Open the browser and go to http://localhost:8501


## Future Improvements

- AI Custom Models
- More Algorithms
- More UI Improvements

&nbsp;

## License

MIT License

### Contributions Welcome - Leave a Star if you like it :star:


