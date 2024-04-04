from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from datetime import datetime
import base64
import os
from PIL import Image
import re

# from imglib import processImg   # for keras and tensorflow

from processimg_fastai import processImg  # for fastai
from mask_tensorflow import get_segmentation_mask

# Initializing flask application
app = Flask(__name__)
cors = CORS(app)

# lesion_lookup = {"mel":"Melanoma (mel)",
#                 "nv":"Melanocytic nevus (nv)",
#                 "bcc":"Basal cell carcinoma (bcc)",
#                 "akiec":"Actinic keratosis / Bowen’s disease (intraepithelial carcinoma) (akiec)",
#                 "bkl":"Benign keratosis (solar lentigo / seborrheic keratosis / lichen planus-like keratosis) (bkl)",
#                 "df":"Dermatofibroma (df)",
#                 "vasc":"Vascular lesion (vasc)"}

lesion_lookup = {"MEL":"Melanoma (mel)",
                "NV":"Melanocytic nevus (nv)",
                "BCC":"Basal cell carcinoma (bcc)",
                "AKIEC":"Actinic keratosis / Bowen’s disease (intraepithelial carcinoma) (akiec)",
                "BKL":"Benign keratosis (solar lentigo / seborrheic keratosis / lichen planus-like keratosis) (bkl)",
                "DF":"Dermatofibroma (df)",
                "VASC":"Vascular lesion (vasc)"}


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
def processRequest():
    try:
        data = request.form["img_content"]
        # print("img_content")
        # print(data[:50])
        pattern = re.compile(r'^data:image/(?P<mime>[a-z]{3,4});base64,(?P<stuff>.+)')
        matchObject = pattern.search(data)
        if matchObject is not None:
            dataDict = matchObject.groupdict()
            if dataDict is not None and 'mime' in dataDict.keys() and 'stuff' in dataDict.keys():
                imgType = dataDict['mime']
                imgBase64 = dataDict['stuff']
                if imgType in ['jpeg', 'png'] and imgBase64 is not None:
                    imgBytes = imgBase64.encode("ascii")
                    decodedBytes = base64.decodebytes(imgBytes)
                    new_filepath = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')
                    #new_filepath = f"{new_filepath}.{imgType}"
                    with open(new_filepath, "wb") as binary_file:
                        # Write bytes to file
                        binary_file.write(decodedBytes)
                    
                    if imgType == 'png':
                        print("convert png to jpg")
                        im = Image.open(new_filepath)
                        rgb_im = im.convert('RGB')
                        jpg_path = f"{new_filepath}.jpg"
                        rgb_im.save(jpg_path, quality=100)
                        os.remove(new_filepath)
                        new_filepath = jpg_path

                    label_name, confidence_percent = processImg(new_filepath)
                    confidence_percent_str = "{:.2f}".format(confidence_percent)
                    print(confidence_percent_str)

                    try:
                        mask = get_segmentation_mask(new_filepath)
                        print(f"mask is {mask}")
                    except:
                        mask = "error.png"
                    
                    os.remove(new_filepath)

                    lesion_name = lesion_lookup.get(label_name)

                    if lesion_name == lesion_lookup.get("MEL"):
                        description = 'Melanoma, is a cancerous lesion. One would have moles with: asymmetrical shape, changes in colour, changes in size, changes in symptoms, and unusual border.'
                    if lesion_name == lesion_lookup.get("NV"):
                        description = 'Nevus, a non-cancerous lesion, is a growth on the skin. No symptoms.'
                    if lesion_name == lesion_lookup.get("BCC"):
                        description = "Basal cell carcinoma is cancerous. They look like shiny, translucent skin colored bumps."
                    if lesion_name == lesion_lookup.get("AKIEC"):
                        description = 'Actinic keratoses and intraepithelial carcinoma is cancerous. They are rough, dry, or scaly patches on skin less \
                        than 1 inch in diameter. They range from pink, red, and brown in colour and itch, burn, bleed, and crust.'
                    if lesion_name == lesion_lookup.get("BKL"):
                        description = 'Benign keratoses is not cancerous. They are itchy, waxy, or rough oval bumps typically on the face, chest, shoulders, or back. \
                            They can have varied numbers of growths and varying colour, ranging from light tan, brown, and black.'
                    if lesion_name == lesion_lookup.get("DF"):
                        description = 'Dermatofibroma are usually not cancerous. They are small, firm bumps which feel like rubbery buttons on the skin surface \
                            Vary from purple to pink and brown to grey in colour. Usually appear on lower legs on middle-aged adults and upper arms in females.'
                    if lesion_name == lesion_lookup.get("VASC"):
                        description = 'Vascular lesions can be both be cancerous and non-cancerous. They can develop in any part of the body, \
                            and may be present as soft tissue mass, pain, swelling, or skin discoloration. They are found in blood vessels and may appear as birthmarks on a baby’s skin.'
                    
                    print(description)
                    print("response normal...")

                    #return predictions
                    return render_template("response.html", lesion_name=lesion_name, confidence_percent_str=confidence_percent_str, description=description,
                                           img_base64_str=imgBase64, 
                                           mask_path = mask)
                                           #mask_base64_str=mask_base64)
            
            print("resopnse file error.")
            return render_template("error.html", error_message="File Processing Error", details="")
    except Exception as ex:
        print("ERROR: ", ex)
        return render_template("error.html", error_message="Server Error", details="{ex}")
    
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)
