# import the necessary packages
from collections import OrderedDict
import numpy as np
import cv2

# define a dictionary that maps the indexes of the facial
# landmarks to specific face regions

#For dlib’s 68-point facial landmark detector:
FACIAL_LANDMARKS_68_IDXS = OrderedDict([
	("mouth", (48, 68)),
	("inner_mouth", (60, 68)),
	("right_eyebrow", (17, 22)),
	("left_eyebrow", (22, 27)),
	("right_eye", (36, 42)),
	("left_eye", (42, 48)),
	("nose", (27, 36)),
	("jaw", (0, 17))
])

#For dlib’s 5-point facial landmark detector:
FACIAL_LANDMARKS_5_IDXS = OrderedDict([
	("right_eye", (2, 3)),
	("left_eye", (0, 1)),
	("nose", (4))
])

FACIAL_LANDMARKS_106_IDXS = OrderedDict([
	("mouth", (84, 96)),
	("inner_mouth", (96, 104)),
	("right_eyebrow", (42, 51)),
	("left_eyebrow", (33, 42)),
	("right_eye", (75, 84)),
	("left_eye", (66, 74)),
	("nose", (51, 66)),
	("jaw", (0, 33))
])



# in order to support legacy code, we'll default the indexes to the
# 68-point model
FACIAL_LANDMARKS_IDXS = FACIAL_LANDMARKS_106_IDXS


def shape_to_np(shape, dtype="int"):
	# initialize the list of (x, y)-coordinates
	coords = np.zeros((shape.num_parts, 2), dtype=dtype)

	# loop over all facial landmarks and convert them
	# to a 2-tuple of (x, y)-coordinates
	for i in range(0, shape.num_parts):
		coords[i] = (shape.part(i).x, shape.part(i).y)

	# return the list of (x, y)-coordinates
	return coords

def visualize_facial_landmarks(image, shape, all_face =False):
	# create two copies of the input image -- one for the
	# overlay and one for the final output image
	overlay = image.copy()
	output = image.copy()

	


	
	cv2.rectangle(overlay, (0, 0), (overlay.shape[1], overlay.shape[0]), (0, 0, 0), -1)
	
	if all_face:
		pts = shape[0:105]


		hull = cv2.convexHull(pts)
		cv2.drawContours(overlay, [hull], -1, (255, 255, 255), -1)



	# loop over the facial landmark regions individually
	for (i, name) in enumerate(FACIAL_LANDMARKS_IDXS.keys()):
		if all_face:
			if  name != "jaw":
				(j, k) = FACIAL_LANDMARKS_IDXS[name]
				pts = shape[j:k]


				hull = cv2.convexHull(pts)
				cv2.drawContours(overlay, [hull], -1, (125, 125, 125), -1)

			if name == "nose":

				(j, k) = FACIAL_LANDMARKS_IDXS[name]
				pts = shape[j:k]


				hull = cv2.convexHull(pts)
				cv2.drawContours(overlay, [hull], -1, (200, 200, 200), -1)


		elif name == "nose" or name == "left_eyebrow"  or name == "right_eyebrow" or name == "mouth":
			(j, k) = FACIAL_LANDMARKS_IDXS[name]
			pts = shape[j:k]

			if name == 'nose':
				for y in range(15):
					if y > 5 and y < 13:
						pts[y][1] += 6

			if name == 'mouth':
				pts[0][0] -= 15

				for y in range(1,6):
					pts[y][1] -= 5
				
				pts[6][0] += 15

				for y in range(7, 12):
					pts[y][1] += 3

			hull = cv2.convexHull(pts)
			cv2.drawContours(overlay, [hull], -1, (255, 255, 255), -1)
			
			


	# cv2.imshow('ww', overlay)
	# cv2.waitKey(0)

	cv2.imwrite('./w.png',overlay)

	return overlay