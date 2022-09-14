from get_face_parts import get_mask
from Ordinary_Procrustes_Analysis import OPA
from poisson_img_editing import poisson_edit
from img2video import img2video
from get_features import return_features
import dlib
import cv2
import time
import numpy as np



s = time.time()

target_name = '21.jpg'
source_name = '94.jpg'



target = cv2.imread('./img/' + target_name)
source = cv2.imread('./img/' + source_name)
    

detector = dlib.get_frontal_face_detector()



rects = detector(target, 0)

if len(rects) > 1:
    print("此照片人數超過一個人，請重新輸入。")
elif len(rects) < 1:
    print("此照片沒有人，請重新輸入。")
else :
    # 把輸入2利用普氏分析法轉至輸入1
    warped_source = OPA(target, source)
    
    cv2.imwrite('./img/warped.png', warped_source)

    print("OPA Cost Time : "+str(time.time() - s))

    #把輸入的器官標記,並選擇較大的mask
    mask = get_mask(target)

    cv2.imwrite('mask.png',mask)


    print("Get Mask Cost Time : "+str(time.time() - s))

    # 利用mask後的輸入1融合在輸入2
    result = poisson_edit(warped_source, target, mask)

    imgs = np.hstack([target,result])



    print("blending Cost Time : " + str(time.time() - s))



    feature_1 = return_features(target)

    feature_2 = return_features(result)

    print(feature_1)


    feature_1 = np.array(feature_1)
    feature_2 = np.array(feature_2)

    

    dist = np.sqrt(np.sum(np.square(feature_1 - feature_2)))
    print(dist)