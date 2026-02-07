import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import torch
torch.set_num_threads(1)

import multiprocessing, sys
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

import open_clip
model, preprocess, tokenizer = open_clip.create_model_and_transforms("ViT-L-14", pretrained="./model/CLIP-ViT-L-14-laion2B-s32B-b82K/open_clip_pytorch_model.bin")
del model, tokenizer

def worker(i):
	for imageName in imageNameChunks[i]:
		try:
			torch.save(preprocess(Image.open(os.path.join(sys.argv[1], imageName)).convert("RGB")), os.path.join(sys.argv[2], imageName))
			print("Pre-processed image %s" % imageName)	# important to keep so progress bar can be updated
		except Exception as e:
			print("Failed to pre-process image %s with error: %s" % (imageName, str(e)), file=sys.stderr)
	return

if __name__ == '__main__':
	procs = []
	for i in range(len(imageNameChunks)):
		p = multiprocessing.Process(target=worker, args=(i,))
		p.start()
		procs.append(p)
	for p in procs:
		p.join()
		if p.exitcode!=0:
			print("Worker died with exit code %d" % (p.exitcode), file=sys.stderr)
