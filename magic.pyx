import random
import cv2
import pinyin


def translate(s):
    ans = ""
    cdef int i
    cdef int st

    for i in range(0, len(s), 2):
        temp = ''
        st = int(s[i : i + 2])
        while st > 0:
            temp = str(st % 9) + temp
            st //= 9
        while len(temp) < 3:
            temp = '0' + temp
        ans += temp
        
    return ans

def create_magic(row):
    cdef list magic = []

    for i in range(256):
        magic.append([])

    cdef int col

    for i in range(256):
        col = row
        for j in range(256):
            magic[i].append(col)
            if col < 8:
                col += 1
            else:
                col = 0
        if row < 6:
            row += 3
        else:
            row = 0
    return magic


def encrypt(img, hide):

    row = random.randint(0, 8)

    magic = create_magic(row)

    cdef list stego_row = []
    cdef list stego_col = []
    cdef int stego_pix_first
    cdef int stego_pix_second

    t_hide = ""

    cdef int i 
    cdef int count

    for s in hide:
        asc = str(ord(s))
        t_hide += asc


    t_hide = translate(t_hide)


    flag = True


    while flag:
        count = 0   
        for i in range(0, len(t_hide)):
            stego_row.append(random.randint(0, len(img) - 2))
            stego_col.append(random.randint(0, len(img[0]) - 2))
        stego_row = sorted(stego_row)
        stego_col = sorted(stego_col)

        for i in range(len(t_hide) - 1):
            if abs(stego_row[i] - stego_row[i + 1]) <= 1:
                if stego_col[i] == stego_col[i + 1]:
                    stego_row = []
                    stego_col = []
                    break
            count += 1

        if count == len(t_hide) - 1:
            flag = False


    location = 0



    for i in range(0, len(t_hide)):

        flag = False

        stego_pix_first = img[stego_col[i]][stego_row[i]][0]
        stego_pix_second = img[stego_col[i]][stego_row[i] + 1][0]

        if stego_pix_first < 1:
            stego_pix_first = 1
        elif stego_pix_first > 254:
            stego_pix_first = 254

        if stego_pix_second < 1:
            stego_pix_second = 1
        elif stego_pix_second > 254:
            stego_pix_second = 254
        

        count = 0

        for j in range(3):
            for k in range(3):
                count += 1
                if magic[stego_pix_first - 1 + j][stego_pix_second - 1 + k] == int(t_hide[i]):
                    img[stego_col[i]][stego_row[i]][0] = stego_pix_first - 1 + j
                    img[stego_col[i]][stego_row[i] + 1][0] = stego_pix_second - 1 + k
                    flag = True
                    break
            if flag:
                break

    cv2.imwrite('./img/fake.png', img)

    img = cv2.imread('./img/fake.png')

    ste = ''


    for i in range(0, len(stego_col)):
        stego_pix_first = img[stego_col[i]][stego_row[i]][0]
        stego_pix_second = img[stego_col[i]][stego_row[i] + 1][0]
        ste += str(magic[stego_pix_first][stego_pix_second])

    ans = ""

    for i in range(0, len(ste), 3):
        ans += chr(int(ste[i : i + 3], 9)) 


    return row, stego_col, stego_row



if __name__ == '__main__':

    id = 'L123456789'
    name = '王昱傑'
    name = pinyin.get(name, format='strip', delimiter="")
    birth = '0881116'
    img = cv2.imread('./img/img39.jpg')

    hide = id + name + birth

    encrypt(img, hide)

     

