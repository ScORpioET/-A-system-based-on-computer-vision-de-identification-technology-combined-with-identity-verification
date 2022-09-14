import numpy as np
import cv2
from get_features import return_features

def extract(img, fake):
    feature = return_features(img)

    str_feature = []

    for i in range(128):
        str_feature.append(str(feature[i]))

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
        


    text = ''

    ans = ''

    Plaintext = ''


    if peak < zero:
        for i in range(fake.shape[0]):
            for j in range(fake.shape[1]):
                if fake[i, j, c] == peak:
                    text += '0'
                if fake[i, j, c] == peak + 1:
                    text += '1'
    else:
        for i in range(fake.shape[0]):
            for j in range(fake.shape[1]):
                if fake[i, j, c] == peak:
                    text += '0'
                if fake[i, j, c] == peak - 1:
                    text += '1'

    for i in range(len(text)):
        if text[i] == '1':
            Plaintext = text[i: len(text)]
            break



    while len(Plaintext) % 4 != 0:
        Plaintext = '0' + Plaintext

    clock = 0

    for i in range(len(Plaintext)):
        if i % 4 == 0:
            text = chr(int('0b011' + Plaintext[i: i + 4], 2))
            
            if clock % 18 == 0:
                if text == '1':
                    ans += '-'
                elif text == '0':
                    ans += '+'
                    
                clock = 1
                continue
            clock += 1

            ans += text
            
    arr = []

    for i in range(len(ans)):
        if ans[i] == '-':
            arr.append('-0.' + ans[i + 1 : i + 18])        
        elif ans[i] == '+':
            arr.append('0.' + ans[i + 1 : i + 18])

    count = 0

    if len(arr) != 128:
        return False

    for i in range(128):
        if arr[i] == str_feature[i]:
            count +=1
        else:
            debug = True
            for j in range(min(len(arr[i]), len(str_feature[i]))):
                if arr[i][j] != str_feature[i][j]:
                    debug = False
                    break
            
            if debug:
                count += 1
            else:
                break

    if count == 128:
        return True
    return False

    

        