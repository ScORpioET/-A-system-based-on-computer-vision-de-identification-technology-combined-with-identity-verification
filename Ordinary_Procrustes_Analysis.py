import cv2
import dlib
import numpy as np

PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
FEATHER_AMOUNT = 11

FACE_POINTS = list(range(17, 68))
MOUTH_POINTS = list(range(48, 61))
RIGHT_BROW_POINTS = list(range(17, 22))
LEFT_BROW_POINTS = list(range(22, 27))
RIGHT_EYE_POINTS = list(range(36, 42))
LEFT_EYE_POINTS = list(range(42, 48))
NOSE_POINTS = list(range(27, 35))
JAW_POINTS = list(range(0, 17))

ALIGN_POINTS = (LEFT_BROW_POINTS + RIGHT_EYE_POINTS + LEFT_EYE_POINTS + RIGHT_BROW_POINTS + NOSE_POINTS + MOUTH_POINTS)

# ALIGN_POINTS = (LEFT_BROW_POINTS + RIGHT_BROW_POINTS + NOSE_POINTS)




class TooManyFaces(Exception):
    pass

class NoFaces(Exception):
    pass    

def get_landmarks(im):

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(PREDICTOR_PATH)

    rects = detector(im, 1)
    


    if len(rects) > 1:
        raise TooManyFaces
    if len(rects) == 0:
        raise NoFaces


    return np.matrix([[p.x, p.y] for p in predictor(im, rects[0]).parts()])

def read_im_and_landmarks(im):
    SCALE_FACTOR = 1 

    im = cv2.resize(im, (im.shape[1] * SCALE_FACTOR,
                         im.shape[0] * SCALE_FACTOR))
    

    s = get_landmarks(im)

    return im, s

def transformation_from_points(points1, points2):
    
    points1 = points1.astype(np.float64)
    points2 = points2.astype(np.float64)
    

    # 69 - 74 是計算平移量

    # np.mean(x) 取x矩陣所有值加起來的均值
    # np.mean(x,axis=0) 取x矩陣每一列的均值
    # np.mean(x,axis=1) 取x矩陣每一行的均值
    c1 = np.mean(points1, axis=0)
    c2 = np.mean(points2, axis=0)


    points1 -= c1
    points2 -= c2

    # 79 - 83 是計算縮放量
 
    # np.std(x)計算x的標準差
    s1 = np.std(points1)
    s2 = np.std(points2)

    points1 /= s1
    points2 /= s2


    # np.linalg.svd(a) a是一個(M,N)矩陣，
    # 返回值 : U大小為(M,M) , S(M,N) , Vt(N,N)
    # S是對a的奇異值分解。S除了對角元素以外都為0，並且對角元素是從大到小排序。
    # 奇異值計算方法 https://ccjou.wordpress.com/2009/09/01/%E5%A5%87%E7%95%B0%E5%80%BC%E5%88%86%E8%A7%A3-svd/
    U, S, Vt = np.linalg.svd(points1.T * points2)

    U2, S2, Vt2 = np.linalg.svd(points1 * points2.T)

    R = (U * Vt).T


    return np.vstack([np.hstack(((s2 / s1) * R,
                                       c2.T - (s2 / s1) * R * c1.T)),
                         np.matrix([0., 0., 1.])])

def warp_im(im, M, dshape):
    output_im = np.zeros(dshape, dtype=im.dtype)

    

    # cv2.warpAffine(輸入圖像,變換矩陣,輸出圖像的大小,dst=輸出圖像)
    cv2.warpAffine(im,
                   M[:2],
                   (dshape[1], dshape[0]),
                   dst=output_im,
                   flags=cv2.WARP_INVERSE_MAP)
    
    
    return output_im


def OPA(source, target, rects=0):
    
    print('Start OPA')

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(PREDICTOR_PATH)

    if (rects == 0):
        num = ''
    else:
        num = str(rects)
        


    im1, landmarks1 = read_im_and_landmarks(source)
    im2, landmarks2 = read_im_and_landmarks(target)



    M = transformation_from_points(landmarks1[ALIGN_POINTS],
                               landmarks2[ALIGN_POINTS])


    

    warped_im = warp_im(im2, M, im1.shape)


    
    print('END OPA')

    return warped_im