import logging, sys, time, os, argparse
from pprint import pprint

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

parser = argparse.ArgumentParser()
parser.add_argument("--web_port", type=int)
cfg = parser.parse_args()

print("vectorizeAudioServer: Loading models...")

#########
# audio # https://huggingface.co/laion/larger_clap_general
#########
import torch, torchaudio
from transformers import ClapModel

model = ClapModel.from_pretrained("./model/larger_clap_general", local_files_only=True).to("cuda").eval()

print("vectorizeAudioServer: Warming up...")
with torch.inference_mode():
    dummy_input = {"input_features": torch.randn(1, 1, 1001, 64).to("cuda")}
    model.get_audio_features(**dummy_input)

def processFilePaths(filePaths):
	results = []
	for filePath in filePaths:
		try:
			inputs = {k: v.to("cuda") for k, v in torch.load(filePath).items()}
			with torch.inference_mode():
				result = model.get_audio_features(**inputs).pooler_output.squeeze().tolist()
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

print("vectorizeAudioServer: Defining flask routes...")

@app.route("/status", methods=["GET"])
def status():
	return "a-ok"

@app.route("/process", methods=["POST"])
def process():
	t0 = time.time()
	results = processFilePaths(request.json["filePaths"])
	print("processFilePaths --- %s seconds ---" % (time.time() - t0))
	return jsonify(results)

print("vectorizeAudioServer: Server running on port: " + str(cfg.web_port))
app.run(host="127.0.0.1", port=cfg.web_port, threaded=False)
