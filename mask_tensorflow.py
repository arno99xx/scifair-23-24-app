import tensorflow.keras.backend as K
import tensorflow as tf
import keras
import cv2
from keras.preprocessing import image
from PIL import Image
import numpy as np
import base64
import os

def get_model():
    unet_model = keras.saving.load_model("saved_models/ISIC_2016/unet_res50/usual_4/exp_1/model", custom_objects={'dice_score': dice_score,
                                                                                                                'iou': iou,
                                                                                                                'dice_loss': dice_loss,
                                                                                                                'jaccard_loss':jaccard_loss,
                                                                                                                'tversky':tversky,
                                                                                                                'focal_tversky_loss': focal_tversky_loss,
                                                                                                                'get_loss': get_loss})
    return unet_model

def get_segmentation_mask(img_path):
    print(f"get_seg_mask {img_path}")
    img_size = 256
    unet_model = get_model()
    the_img = image.load_img(img_path, target_size=(img_size, img_size))
    img_1 = np.array(the_img)
    img_1 = img_1 / (img_size-1)
    img_1 = img_1.reshape((1,img_size,img_size,3))
    
    result = unet_model.predict(img_1)

    x = result[0,:, :, :]
    arr = x * (img_size - 1)
    #arr = np.ascontiguousarray(arr.transpose(1,2,0))
    im = Image.fromarray(arr, 'RGBA')
    #mask_path = f"{img_path}.png"
    mask_path = f"{img_path}.png"
    print(f"saving {mask_path}")
    im.save("static/" + mask_path)
    # with open(mask_path, "rb") as f:
    #     encoded_image = base64.b64encode(f.read())
    # os.remove(mask_path)
    # print(encoded_image)
    # return encoded_image
    return mask_path


def iou(y_true, y_pred):
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    union = K.sum(y_true_f) + K.sum(y_pred_f) - intersection
    return intersection / union


def dice_score(y_true, y_pred):
    smooth = 1.
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    score = (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)
    return score




# Dice loss according dice coefficient
def dice_loss(y_true, y_pred):
    loss = 1 - dice_score(y_true, y_pred)
    return loss


# Jacard loss
def jaccard_loss(output, target, axis=(0, 1, 2), smooth=1e-5):
    inse = tf.reduce_sum(output * target, axis=axis)
    l = tf.reduce_sum(output * output, axis=axis)
    r = tf.reduce_sum(target * target, axis=axis)
    jaccard = 1 - (inse + smooth) / (l + r - inse + smooth)
    jaccard = tf.reduce_mean(jaccard)
    return jaccard


# Tversky index
def tversky(y_true, y_pred):
    y_true_pos = K.flatten(y_true)
    y_pred_pos = K.flatten(y_pred)
    true_pos = K.sum(y_true_pos * y_pred_pos)
    false_neg = K.sum(y_true_pos * (1 - y_pred_pos))
    false_pos = K.sum((1 - y_true_pos) * y_pred_pos)
    alpha = 0.7
    return (true_pos + 1) / (true_pos + alpha * false_neg + (1 - alpha) * false_pos + 1)


# Focal loss according to tversky index
def focal_tversky_loss(y_true, y_pred):
    pt_1 = tversky(y_true, y_pred)
    gamma = 0.75
    return K.pow((1 - pt_1), gamma)


def get_loss(loss_name, logger=None):
    if loss_name == 'dice_loss':
        loss = dice_loss
    elif loss_name == 'jaccard_loss':
        loss = jaccard_loss
    elif loss_name == 'focal_tversky_loss':
        loss = focal_tversky_loss
    else:
        print(f"loss_name: {loss_name} is not supported!")
    print(f"loss: {loss_name} is successfully created!")
    #else:
        #value_error_log(logger, f"loss_name: {loss_name} is not supported!")
    #log_print(logger, f"loss: {loss_name} is successfully created!")
    return loss

