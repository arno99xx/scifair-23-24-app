import fastai
# from fastai.vision import *
from fastai.vision.core import *
from fastai.vision.augment import *
from fastai.vision.data import *
from fastai.data.transforms import *
from fastai.vision.all import *
import numpy as np
import pandas as pd

# from keras.utils import img_to_array
# from keras.models import load_model
# import cv2

from flask_cors import CORS, cross_origin

# import tensorflow as tf

from datetime import datetime

import base64
import os

from PIL import Image
import re

#names = ["daisy", "dandelon", "roses", "sunflowers", "tulips"]
class_names = ["mel", "nv", "bcc", "akiec", "bkl", "df", "vasc"]

# Process image and predict label
def processImg(img_path):
    learn_inf = load_learner('export.pkl')
    # print(learn_inf.model)
    # print(learn_inf.dls.vocab)
    with learn_inf.no_bar():
        result = learn_inf.predict(img_path)
    label_name = result[0]
    idx = result[1].numpy()
    score = result[2][idx]
    # print(f"idx = {idx}, score = {score}")
    confidence_percent = 100 * score
    # max_score = np.max(result[2].numpy())
    # print(f"max_score = {max_score}")
    # assert max_score == score
    return label_name, confidence_percent

def processImg_with_inf(img_path, learn_inf):
    with learn_inf.no_bar():
        result = learn_inf.predict(img_path)
    label_name = result[0]
    idx = result[1].numpy()
    score = result[2][idx]
    confidence_percent = 100 * score
    return label_name, confidence_percent

def get_inf():
    learn_inf = load_learner('export.pkl')
    #learn_inf.recorder.silent = True
    return learn_inf