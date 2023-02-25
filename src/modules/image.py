import imutils
import urllib
import cv2 as cv2
import numpy as np
from PIL import Image
import albumentations as A

transform = A.Compose([
    A.RandomCropFromBorders(always_apply=False, p=1.0, crop_left=0.1, crop_right=0.1, crop_top=0.1, crop_bottom=0.1),
    A.RandomBrightnessContrast(always_apply=False, p=1.0, brightness_limit=(-0.2, 0.2), contrast_limit=(-0.2, 0.2), brightness_by_max=True),
    A.RandomToneCurve(always_apply=False, p=1.0, scale=0.1)
])

def resize_image(img, scale_percent=65):
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    
    # resize image
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    return resized
    
def download_image(list_url_images, keyword, path='images/'):
    list_filename = list()
    for idx, url_image in enumerate(list_url_images):
        try:
            url_response = urllib.request.urlopen(url_image)
            image_arr = np.array(bytearray(url_response.read()), dtype=np.uint8)
            image = cv2.imdecode(image_arr, -1)
            # image resize
            w, h = image.shape[:2]
            if w > h: image = imutils.resize(image, width=1000)
            else: image = imutils.resize(image, height=1000)
            # if w >=1000 or h>=1000:
            #     image = resize_image(image, 30)
            # processing image
            image_trans = transform(image=image)['image']
            # add watermark
            # height, width = image_trans.shape[:2]
            # text = 'Artistic Interiors'
            # cv2.putText(image_trans, text, (15, height - 15), cv2.FONT_ITALIC, 0.5, (255,255,255), 1)

            filename = f"{keyword.replace(' ', '_')}_{idx+1}.png"
            saved = cv2.imwrite('images/'+filename, image_trans)
            if saved: list_filename.append(filename)
            else: continue
        except:
            continue
    return list_filename