import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import torch
torch.set_num_threads(1)

import multiprocessing, sys
from pprint import pprint

fileNames = []
for root, dirs, files in os.walk(sys.argv[1]):
	for fileName in files:
		fileNames.append(fileName)

numPerChunk = int(len(fileNames)/os.cpu_count())+1
fileNameChunks = [fileNames[x:x+numPerChunk] for x in range(0, len(fileNames), numPerChunk)]

import torchaudio
from transformers import ClapProcessor
processor = ClapProcessor.from_pretrained("./model/larger_clap_general", local_files_only=True)

def worker(i):
	for fileName in fileNameChunks[i]:
		try:
			audio, sr = torchaudio.load(os.path.join(sys.argv[1], fileName))
			if sr != 48000:
				audio = torchaudio.functional.resample(audio, sr, 48000)
			mono = audio.mean(dim=0, keepdim=True)[0].numpy()
			inputs = processor(audio=mono, sampling_rate=48000, return_tensors="pt")
			torch.save(inputs.data, os.path.join(sys.argv[2], fileName))
			print("Pre-processed audio %s" % fileName)	# important to keep so progress bar can be updated
		except Exception as e:
			print("Failed to pre-process audio file %s with error: %s" % (fileName, str(e).replace('\n', ' ').strip()), file=sys.stderr)
	return

if __name__ == '__main__':
	procs = []
	for i in range(len(fileNameChunks)):
		p = multiprocessing.Process(target=worker, args=(i,))
		p.start()
		procs.append(p)
	for p in procs:
		p.join()
		if p.exitcode!=0:
			print("Worker died with exit code %d" % (p.exitcode), file=sys.stderr)
