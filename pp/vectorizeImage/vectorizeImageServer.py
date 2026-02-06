import logging, sys, time, os, argparse
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument("--web_port", type=int)
cfg = parser.parse_args()

print("vectorizeImageServer: Loading models...")

#############
# vectorize # https://huggingface.co/laion/CLIP-ViT-L-14-laion2B-s32B-b82K
#############
import torch, open_clip

vectorizeModel, preprocess, _ = open_clip.create_model_and_transforms("ViT-L-14", pretrained="./model/CLIP-ViT-L-14-laion2B-s32B-b82K/open_clip_pytorch_model.bin")
vectorizeModel.to("cuda")
vectorizeModel.eval()

print("vectorizeImageServer: Warming up...")
with torch.inference_mode():
    dummy = torch.randn(1, 3, 224, 224).to("cuda")
    vectorizeModel.encode_image(dummy)

def processFilePaths(filePaths):
	results = []
	for filePath in filePaths:
		try:
			img = torch.load(filePath).unsqueeze(0).to("cuda")
			with torch.inference_mode():
				result = vectorizeModel.encode_image(img)[0].cpu().tolist()
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

print("vectorizeImageServer: Defining flask routes...")

@app.route("/status", methods=["GET"])
def status():
	return "a-ok"

@app.route("/process", methods=["POST"])
def process():
	t0 = time.time()
	results = processFilePaths(request.json["filePaths"])
	print("processFilePaths --- %s seconds ---" % (time.time() - t0))
	return jsonify(results)

print("vectorizeImageServer: Server running on port: " + str(cfg.web_port))
app.run(host="127.0.0.1", port=cfg.web_port, threaded=False)
