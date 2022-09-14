import numpy as np
import cv2
import scipy.sparse
from scipy.sparse.linalg import spsolve
import time


def laplacian_matrix(n, m):
    
# 建立m*m的全0矩陣
    mat_D = scipy.sparse.lil_matrix((m, m))


# 塞入對角線內,ex:(-1,-2)代表在矩陣[0][2]為起點的對角線放入-1
#               (-1,2)代表在矩陣[2][0]為起點的對角線放入-1

    mat_D.setdiag(4)

    
    # print(mat_D.todense())

        
    mat_A = scipy.sparse.block_diag([mat_D] * n).tolil()
    mat_A.setdiag(-1, -1)
    mat_A.setdiag(-1, 1)
    mat_A.setdiag(-1, 1 * m)
    mat_A.setdiag(-1, -1 * m)
    

    
    return mat_A


def poisson_edit(source, target, mask, offset=(0, 0)):

    print("Start poisson_edit")

    result = target.copy()





    y_max, x_max = result.shape[:-1]
    y_min, x_min = 0, 0

    x_range = x_max - x_min
    y_range = y_max - y_min
    
    mat_A = laplacian_matrix(y_range, x_range)


    s = time.time()
    # for \Delta g
    laplacian = mat_A.tocsc()




    # set the region outside the mask to identity    
    for y in range(0, y_range - 1):
        for x in range(0, x_range):
            if mask[y, x] == 0:
                k = x + y * x_range
            mat_A[k, k] = 1
            if k != x_range * x_range - 1:
                mat_A[k, k + 1] = 0
            mat_A[k, k - 1] = 0
            if k < x_range * x_range - x_range:
                mat_A[k, k + x_range] = 0
            mat_A[k, k - x_range] = 0

    # corners
    # mask[0, 0]
    # mask[0, y_range-1]
    # mask[x_range-1, 0]
    # mask[x_range-1, y_range-1]

    mat_A = mat_A.tocsc()


# flatten把多維變成1一維
    mask_flat = mask.flatten()
    
    for channel in range(source.shape[2]):
        source_flat = source[y_min:y_max, x_min:x_max, channel].flatten()
        result_flat = result[y_min:y_max, x_min:x_max, channel].flatten()


        #concat = source_flat*mask_flat + result_flat*(1-mask_flat)
        
        # inside the mask:
        # \Delta f = div v = \Delta g
        # laplacian*source_flat  
        alpha = 1
        mat_b = laplacian.dot(source_flat) * alpha
        
        # outside the mask:
        # f = t
        mat_b[mask_flat == 0] = result_flat[mask_flat == 0]
        
        
        x = spsolve(mat_A, mat_b)
        

        #print(x.shape)
        x = x.reshape((y_range, x_range))



        #print(x.shape)
        x[x > 255] = 255
        x[x < 0] = 0
        x = x.astype('uint8')
        #x = cv2.normalize(x, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        #print(x.shape)

        result[y_min:y_max, x_min:x_max, channel] = x

    cv2.imwrite('./img/result.jpg', result)

    print("End poisson_edit")

    return  result
