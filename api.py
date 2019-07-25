from face_recognition import face_locations, face_encodings, face_distance, load_image_file
from numpy import argmin
import time
class NoFaceDetectedError(Exception):
	pass

#input: an image that contains exactly one face
#output: the encoding of that face
#exception: if no face detected, raise NoFaceDetectedError
def train(file_stream):
	image = load_image_file(file_stream)
	location = face_locations(image)
	if not location:
		raise NoFaceDetectedError()
	encodings = face_encodings(image, location)
	return encodings[0]

#input: an image that contains exactly one face
#input: a dictionary represent the encodings we knew
#output: a tuple with format (top, right, bottom, left, name)
def identify(image, known_dict):
	locations = face_locations(image)
	if not locations:
		raise NoFaceDetectedError()
	unknown_encoding = face_encodings(image, locations)[0]
	distances = face_distance(list(known_dict.values()), unknown_encoding)
	if distances.size == 0:
		return None
	index = argmin(distances)
	if distances[index] <= 0.4:

		return list(known_dict.keys())[index]
	else:
		return None

