import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys
import time
from get_features import return_features



def Feature2Cipher(f):

    Ciphertext = ''
    d = 0
    text = ''

    for i in range(len(f)):

        

        if f[i][0] == '-':
            text = ('1' + f[i][3:20])
            d = 3
        else: 
            text = ('0' + f[i][2:19])
            d = 2

        while len(text) < 18:
            text += '0'


        for j in range(len(text)):
            asc = (str(bin(ord(text[j])))[4:])

            while len(asc) < 4:
                asc = '0' + asc
            Ciphertext += asc

    return Ciphertext

def Text2Binary(t):
    pass

def embed(img, feature):

    feature_arr = ''

    for i in range(128):
        if i == 0:
            feature_arr += str(feature[i])
        else:
            feature_arr += ',' + str(feature[i])

    feature_arr = feature_arr.split(',')
    Ciphertext = Feature2Cipher(feature_arr)


    r_num = np.zeros(256, dtype='int64')
    g_num = np.zeros(256, dtype='int64')
    b_num = np.zeros(256, dtype='int64')


    zero_num = img.shape[0] * img.shape[1] + 1
    peak = -1
    peak_num = 0
    zero = 256


    text = ''

    r = False
    g = False
    b = False

    r_min = img.shape[0] * img.shape[1] + 1
    g_min = img.shape[0] * img.shape[1] + 1
    b_min = img.shape[0] * img.shape[1] + 1


    text = ''
 

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            r_num[img[i, j, 2]] += 1
            g_num[img[i, j, 1]] += 1
            b_num[img[i, j, 0]] += 1


    for i in range(256):
        if r_min > r_num[i]:
            r_min = r_num[i]
        if g_min > g_num[i]:
            g_min = g_num[i]
        if b_min > b_num[i]:
            b_min = b_num[i]

        if r_num[i] == 0:
            r = True    
            c = 2
            num = r_num
            break
        if g_num[i] == 0:
            g = True
            c = 1
            num = g_num
            break
        if b_num[i] == 0:
            b = True
            c = 0
            num = b_num
            break

    if not (r or g or b):
        if r_min <= g_min and r_min <= b_min:
            num = r_num
            c = 2
        if g_min <= r_min and g_min <= b_min:
            num = g_num
            c = 1
        if b_min <= g_min and b_min <= r_min:
            num = b_num
            c = 0
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i, j, c] == zero:
                    if zero == 0:
                        img[i, j, c] += 1
                    else:
                        img[i, j, c] -= 1




        
    for i in range(len(num)):
        if num[i] > peak_num:
            peak = i
            peak_num = num[i]
        if num[i] < zero_num:
            zero = i
            zero_num = num[i]
            
    if c == 0:
        print('color = blue')
    elif c == 1:
        print('color = green')
    elif c == 2:
        print('color = red')


    print('peak = ', str(peak))
    print('zero = ', str(zero))


    length = np.arange(len(num))

    # plt.bar(length, num, tick_label = num)
    # plt.show()            


    if len(Ciphertext) < peak_num:
        z = ''
        for i in range(peak_num - len(Ciphertext)):
            z += '0'
        Ciphertext = z + Ciphertext


    if zero > peak:
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i, j, c] < zero and img[i, j, c] > peak:
                    img[i, j, c] += 1
        count = 0   

        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i, j, c] == peak:
                    if Ciphertext[count] == '1':
                        img[i, j, c] += 1
                        
                    count += 1
    else:        
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i, j, c] > zero and img[i, j, c] < peak:
                    img[i, j, c] -= 1
        count = 0


        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if img[i, j, c] == peak:
                    
                    if Ciphertext[count] == '1':
                        img[i, j, c] -= 1
                    count += 1
                    

    cv2.imwrite('embed.png', img)


    length = np.arange(len(num))

    # plt.bar(length, num, tick_label = num)
    # plt.show()

    # print(peak_num/512/512)
    if c == 0:
        print('color = blue')
    elif c == 1:
        print('color = green')
    elif c == 2:
        print('color = red')


    print('peak = ', str(peak))
    print('zero = ', str(zero))

    return img


if __name__ == '__main__':
    img = cv2.imread('./img/65.jpg')
    embed(img,return_features(img))