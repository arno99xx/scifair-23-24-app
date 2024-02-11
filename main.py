from flask import Flask, render_template, request
from keras.preprocessing.image import img_to_array
from keras import layers
from keras.applications import VGG19

from keras.models import load_model
from keras import Model
import cv2
import numpy as np

import tensorflow as tf

from flask_cors import CORS, cross_origin

names = ["Melanoma", "Melanocytic nevus", "Basal cell carcinoma", "Actinic keratosis / Bowen’s disease (intraepithelial carcinoma)", 
         "Benign keratosis (solar lentigo / seborrheic keratosis / lichen planus-like keratosis)", "Dermatofibroma", "Vascular lesion"]
model = None

def cls_model(input_shape):
    inputs = layers.Input(shape=input_shape)
    vgg19 = VGG19(include_top=False, weights="imagenet", input_tensor=inputs)
    x = vgg19(inputs, training=False)
    
    x = layers.Conv2D(64, 3, padding="same")(x)
    x = layers.Activation("relu")(x)
    x = layers.BatchNormalization()(x)
    #classi layers
    for filters in [96, 128, 256]:#, 320]:#, 512]:#, 1024, 2048]:
        x = layers.Conv2D(filters, 3, padding="same")(x)
        x = layers.Activation("relu")(x)
        x = layers.BatchNormalization()(x)

        x = layers.Conv2D(filters, 3, padding="same")(x)
        x = layers.Activation("relu")(x)
        x = layers.BatchNormalization()(x)

        x = layers.MaxPool2D(3, strides=2, padding="same")(x)

    #output
    x = layers.Dropout(rate=0.3)(x)
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation="sigmoid")(x)

    output = layers.Dense(7, activation="softmax")(x)

    model = Model(inputs=inputs, outputs=output, name="classification")
    return model

# Process image and predict label
def processImg(IMG_PATH):
    # Preprocess image
    image = np.array(cv2.imread(IMG_PATH))
    image = cv2.resize(image, (256, 256))
    print(image.shape)

    res = model.predict(image[None, :, :, :])
    print(res)
    label = np.argmax(res)
    print(label)
    total_label_score = np.sum(res[0])
    ind_label_score = res[0][label]
    final_score = np.round(ind_label_score/total_label_score, 2)
    global names
    print("Label", label)
    labelName = names[label]
    print("Label name:", labelName)
    return labelName, final_score


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
    global model
    if model is None:
        model = cls_model((256,256,3))
        model.load_weights("final_class.h5")
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        tflite_model = converter.convert()
        
        # Save the model.
        with open(str("final_class"), 'wb') as f:
            f.write(tflite_model)
    data = request.files["fileToUpload"]
    data.save("img.jpg")

    lesion, score = processImg("img.jpg")


    #return flower_name
    return render_template("response.html", lesion=lesion, score=score)


if __name__ == "__main__":
    app.run(debug=True)
