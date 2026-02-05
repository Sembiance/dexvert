import os, multiprocessing, sys
from pprint import pprint

imageNames = []

for root, dirs, files in os.walk(sys.argv[1]):
	for imageName in files:
		imageNames.append(imageName)

numPerChunk = int(len(imageNames)/os.cpu_count())+1
imageNameChunks = [imageNames[x:x+numPerChunk] for x in range(0, len(imageNames), numPerChunk)]

from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None
import tensorflow as tf
import torch
from opennsfw2._image import preprocess_image, Preprocessing

def worker(i):
	for imageName in imageNameChunks[i]:
		try:
			torch.save(tf.convert_to_tensor(preprocess_image(Image.open(os.path.join(sys.argv[1], imageName)), Preprocessing.YAHOO)), os.path.join(sys.argv[2], imageName))
			print("Pre-processed image %s" % imageName)	# important to keep so progress bar can be updated
		except Exception as e:
			print("Failed to pre-process image %s with error: %s" % (imageName, str(e)))
	return

if __name__ == '__main__':
	procs = []
	for i in range(len(imageNameChunks)):
		p = multiprocessing.Process(target=worker, args=(i,))
		p.start()
		procs.append(p)
	for p in procs:
		p.join()
