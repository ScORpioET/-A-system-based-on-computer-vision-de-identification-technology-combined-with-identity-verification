# import the necessary packages
from imutils import face_utils
import numpy as np
import argparse
import imutils
import dlib
import cv2


def Compare(mask1, mask2):

	y_max, x_max = mask1.shape[:-1]

	mask1 = cv2.cvtColor(mask1, cv2.COLOR_BGR2GRAY)
	mask2 = cv2.cvtColor(mask2, cv2.COLOR_BGR2GRAY)


	count1 = 0
	count2 = 0
	for y in range(1, y_max - 1):
		for x in range(1, x_max - 1):
			if mask1[y, x] == 255:
				count1 += 1
			if mask2[y, x] == 255:
				count2 += 1
				
	if count1 > count2:
		return mask1
	
	if count1 < count2:
		return mask2

	return mask1


def get_mask(img1, rects = 0):

	print("Start get_mask")

	if (rects == 0):
		num = ''
	else:
		num = str(rects)

	detector = dlib.get_frontal_face_detector()
	predictor = dlib.shape_predictor("./shape_predictor_106_face_landmarks.dat")
	# load the input image, resize it, and convert it to grayscale
	# image = cv2.imread('./img/warped_' + target_name)

	

	gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)


	# detect faces in the grayscale image
	rects = detector(gray1, 1)
	for (i, rect) in enumerate(rects):

		shape = predictor(gray1, rect)
		
		shape = face_utils.shape_to_np(shape)

		mask1 = face_utils.visualize_facial_landmarks(img1, shape)

		mask1 = cv2.cvtColor(mask1, cv2.COLOR_BGR2GRAY)

		print(mask1)

		cv2.imwrite('a.png',mask1)

	return mask1

if __name__ == "__main__":
    get_mask(cv2.imread("./img/65.jpg"),0)
