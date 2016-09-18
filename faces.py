"""Draws squares around faces in the given image."""

import argparse
import base64

from PIL import Image
from PIL import ImageDraw

from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials




# [START get_vision_service]
DISCOVERY_URL='https://{api}.googleapis.com/$discovery/rest?version={apiVersion}'


def get_vision_service():
	credentials = GoogleCredentials.get_application_default()
	return discovery.build('vision', 'v1', credentials=credentials,
						   discoveryServiceUrl=DISCOVERY_URL)
# [END get_vision_service]


# [START detect_face]
def detect_face(face_file, max_results=4):
	"""Uses the Vision API to detect faces in the given file.
	Args:
		face_file: A file-like object containing an image with faces.
	Returns:
		An array of dicts with information about the faces in the picture.
	"""
	image_content = face_file.read()
	batch_request = [{
		'image': {
			'content': base64.b64encode(image_content).decode('UTF-8')
			},
		'features': [{
			'type': 'FACE_DETECTION',
			'maxResults': max_results,
			}]
		}]

	service = get_vision_service()
	request = service.images().annotate(body={
		'requests': batch_request,
		})
	response = request.execute()

	return response['responses'][0]['faceAnnotations']
# [END detect_face]


# [START highlight_faces]
def highlight_faces(image, faces, output_filename):
	"""Draws a polygon around the faces, then saves to output_filename.
	Args:
	  image: a file containing the image with the faces.
	  faces: a list of faces found in the file. This should be in the format
		  returned by the Vision API.
	  output_filename: the name of the image file to be created, where the faces
		  have polygons drawn around them.
	"""
	print(image)
	im = Image.open(image)
	draw = ImageDraw.Draw(im)


	for face in faces:
		box = [(v.get('x', 0.0), v.get('y', 0.0)) for v in face['fdBoundingPoly']['vertices']]
		fill = '#00ff00'

		print (face['joyLikelihood'])
		print (face['surpriseLikelihood'])
		print (face['sorrowLikelihood'])
		print (face['angerLikelihood'])
		

		if face['joyLikelihood'] == 'VERY_LIKELY' or face['joyLikelihood'] == 'LIKELY' or face['joyLikelihood'] == 'POSSIBLE':
			icon = Image.open("happy.png")			
		if face['sorrowLikelihood'] == 'VERY_LIKELY' or face['sorrowLikelihood'] == 'LIKELY' or face['sorrowLikelihood'] == 'POSSIBLE':
			icon = Image.open("sad.png")
		if face['angerLikelihood'] == 'VERY_LIKELY' or face['angerLikelihood'] == 'LIKELY' or face['angerLikelihood'] == 'POSSIBLE':
			icon = Image.open("angry.png")
		if face['surpriseLikelihood'] == 'VERY_LIKELY' or face['surpriseLikelihood'] == 'LIKELY' or face['surpriseLikelihood'] == 'POSSIBLE':
			icon = Image.open("surprise.png")
		
		x, y = icon.size
		icon = icon.resize((abs(box[0][0]-box[1][0]),abs(box[0][1]-box[3][1])))
		im.paste(icon, box[0], mask=icon)

		# draw.line(box + [box[0]], width=5, fill=fill)

	# del draw
	im.save(output_filename)
# [END highlight_faces]


# [START main]
def main(input_filename, output_filename, max_results):
	with open(input_filename, 'rb') as image:
		faces = detect_face(image, max_results)
		
		print('Found %s face%s' % (len(faces), '' if len(faces) == 1 else 's'))

		print('Writing to file %s' % output_filename)
		# Reset the file pointer, so we can read the file again
		image.seek(0)
		highlight_faces(image, faces, output_filename)

# [END main]


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Detects faces in the given image.')
	parser.add_argument(
		'input_image', help='the image you\'d like to detect faces in.')
	parser.add_argument(
		'--out', dest='output', default='out.jpg',
		help='the name of the output file.')
	parser.add_argument(
		'--max-results', dest='max_results', default=4,
		help='the max results of face detection.')
	args = parser.parse_args()

	main(args.input_image, args.output, args.max_results)