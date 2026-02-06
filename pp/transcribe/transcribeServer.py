import logging, sys, time, os, argparse
from pprint import pprint
import warnings
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TQDM_DISABLE"] = "1"
warnings.filterwarnings("ignore", message=".*torch.cuda.amp.autocast.*")

parser = argparse.ArgumentParser()
parser.add_argument("--web_port", type=int)
cfg = parser.parse_args()

print("transcribeServer: Loading models...")

##############
# Transcribe # https://github.com/openai/whisper/discussions/662#discussioncomment-9086887
##############
import whisper_s2t

model = whisper_s2t.load_model(model_identifier="medium.en", backend="CTranslate2")

def processFilePaths(filePaths):
	try:
		results = model.transcribe(filePaths, lang_codes=["en"], tasks=["transcribe"], initial_prompts=[None], batch_size=32)
		return results

	except Exception as e:
		print("BATCH Failed to transcribe audio with error: %s\nPerforming audio transcriptions 1 at a time..." % (str(e)))
		results = []
		for filePath in filePaths:
			try:
				result = model.transcribe([filePath], lang_codes=["en"], tasks=["transcribe"], initial_prompts=[None], batch_size=32)
				results.append(result)
			except Exception as e:
				print("Failed to transcribe audio with error: %s" % (str(e)) + " for file: " + filePath)
				results.append({"err" : str(e)})
		return results

################
# FLASK ROUTES #
################
from flask import Flask, request, jsonify
app = Flask(__name__)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

print("transcribeServer: Defining flask routes...")

@app.route("/status", methods=["GET"])
def status():
	return "a-ok"

@app.route("/process", methods=["POST"])
def process():
	t0 = time.time()
	results = processFilePaths(request.json["filePaths"])
	print("processFilePaths --- %s seconds ---" % (time.time() - t0))
	return jsonify(results)

print("transcribeServer: Server running on port: " + str(cfg.web_port))
app.run(host="127.0.0.1", port=cfg.web_port, threaded=False)
