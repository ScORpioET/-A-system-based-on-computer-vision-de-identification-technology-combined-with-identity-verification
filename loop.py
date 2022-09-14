from get_face_parts import get_mask
from Ordinary_Procrustes_Analysis import OPA
from poisson_img_editing import poisson_edit
from img2video import img2video
from get_features import return_features
import dlib
import cv2
import time
import numpy as np
from os import listdir
from os.path import isfile, isdir, join




imgpath = "./img/21"

files = listdir(imgpath)

# 以迴圈處理
for f in files:
  # 產生檔案的絕對路徑
  fullpath = join(imgpath, f)
  img = cv2.imread(fullpath)

  img = cv2.resize(img,(400,400))

  cv2.imwrite(fullpath,img)