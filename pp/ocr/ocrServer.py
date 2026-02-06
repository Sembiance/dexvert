import logging, sys, time, os, argparse
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument("--web_port", type=int)
cfg = parser.parse_args()

print("ocrServer: Loading models...")

#######
# OCR # https://github.com/mindee/doctr
#######
import torch
import numpy as np
from doctr.models import ocr_predictor

model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True).cuda()

print("ocrServer: Warming up...")
with torch.inference_mode():
    dummy = np.zeros((100, 100, 3), dtype=np.uint8)
    model([dummy])

def processFilePaths(filePaths):
	# Can't call from_images(filePaths) with entire list because the images are different dimensions
	results = []
	for filePath in filePaths:
		try:
			with torch.inference_mode():
				result = model([np.load(filePath)]).export()
			results.append(result)
		except Exception as e:
			results.append({"err" : str(e)})
	return results

################
# FLASK ROUTES #
################
from flask import Flask, request, jsonify
app = Flask(__name__)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

print("ocrServer: Defining flask routes...")

@app.route("/status", methods=["GET"])
def status():
	return "a-ok"

@app.route("/process", methods=["POST"])
def process():
	t0 = time.time()
	results = processFilePaths(request.json["filePaths"])
	print("processFilePaths --- %s seconds ---" % (time.time() - t0))
	return jsonify(results)

print("ocrServer: Server running on port: " + str(cfg.web_port))
app.run(host="127.0.0.1", port=cfg.web_port, threaded=False)
