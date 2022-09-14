import cv2
import numpy as np

def img2video(img):
    
    img_array = []

    height, width, layers = img.shape
    size = (width, height)
    for i in range(10):
        img_array.append(img)
    
    
    out = cv2.VideoWriter('data/video_img/project.avi',cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
    
    for i in range(len(img_array)):
        out.write(img_array[i])

    out.release()