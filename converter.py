#%%
import cv2
from PIL import Image
import pytesseract
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
# %%
config = r'-l por+eng --psm 6'

def plot(img):
    plt.figure(figsize = (12,16))
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()

# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# noise removal
def remove_noise(image):
    return cv2.medianBlur(image,5)
 
#thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#dilation
def dilate(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(image, kernel, iterations = 1)
    
#erosion
def erode(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)

#opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

#canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)

#skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

#template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED) 

# %%
def ocr(imgpath):
    print('doing '+imgpath+'\n')
    img = cv2.imread(imgpath )
    gray = get_grayscale(img)
    thresh = thresholding(gray)
    df = pytesseract.image_to_data(imgpath, output_type='data.frame',config=config)
    return df
# %%
def create_db():
    full_df = pd.DataFrame([])
    for r,d,f in os.walk(os.path.join(os.getcwd(),'papers','imgs')):
        for file in f:
            print(file)
            try:
                df = ocr(os.path.join(r,file))
                df['file'] = r.split(os.sep)[-2]+"|"+r.split(os.sep)[-2]+'|'+file
                full_df = full_df.append(df,ignore_index=True)
            except:
                print('Error on file '+file)
    full_df.to_csv('full_df.csv',encoding='utf-8')


#%%
