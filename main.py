from flask import Flask, render_template, request
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import cv2
import numpy as np

from flask_cors import CORS, cross_origin

names = ["Melanoma", "Melanocytic nevus", "Basal cell carcinoma", "Actinic keratosis / Bowen’s disease (intraepithelial carcinoma)", 
         "Benign keratosis (solar lentigo / seborrheic keratosis / lichen planus-like keratosis)", "Dermatofibroma", "Vascular lesion"]



# Process image and predict label
def processImg(IMG_PATH):
    # Read image
    model = load_model("final_class.h5")
    
    # Preprocess image
    image = cv2.imread(IMG_PATH)
    image = cv2.resize(image, (256, 256))
    image = image.astype("float16") / 255.0
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)

    res = model.predict(image[None,])
    print(res)
    label = np.argmax(res)
    label_score = res[label]

    print("Label", label)
    labelName = names[label]
    print("Label name:", labelName)
    return labelName, label_score


# Initializing flask application
app = Flask(__name__)
cors = CORS(app)

@app.route("/")
def main():
    # return """
    #     Application is working
    # """
    return render_template("index.html")

# About page with render template
@app.route("/about")
def postsPage():
    return render_template("about.html")

# Process images
@app.route("/process", methods=["POST"])
def processReq():
    data = request.files["fileToUpload"]
    data.save("img.jpg")

    lesion, score = processImg("img.jpg")


    #return flower_name
    return render_template("response.html", lesion=lesion, score=score)


if __name__ == "__main__":
    app.run(debug=True)
