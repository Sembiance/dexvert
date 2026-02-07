import logging, sys, time, os, argparse
from pprint import pprint

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "1"
os.environ["TF_XLA_FLAGS"] = "--tf_xla_auto_jit=2"

parser = argparse.ArgumentParser()
parser.add_argument("--web_port", type=int)
cfg = parser.parse_args()

print("nsfwServer: Loading models...")

########
# NSFW # https://pypi.org/project/opennsfw2/
########
import numpy as np
import tensorflow as tf
from opennsfw2._model import make_open_nsfw_model
from concurrent.futures import ThreadPoolExecutor

nsfwModel = make_open_nsfw_model(weights_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "weights", "open_nsfw_weights-0.1.0.h5"))

print("nsfwServer: Warming up...")
dummy = tf.zeros((1, 224, 224, 3))
nsfwModel.predict(dummy, verbose=0)

def processFilePaths(filePaths):
	images = np.empty((len(filePaths), 224, 224, 3), dtype=np.float32)
	def _load(args):
		i, fp = args
		images[i] = np.load(fp + ".npy")
	with ThreadPoolExecutor(max_workers=8) as ex:
		list(ex.map(_load, enumerate(filePaths)))
	results = []
	for i in range(0, len(images), 64):
		preds = nsfwModel(images[i:i+64], training=False)
		results.extend((preds[:, 1].numpy() * 100).tolist())
	return results

################
# FLASK ROUTES #
################
from flask import Flask, request, jsonify
app = Flask(__name__)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

print("nsfwServer: Defining flask routes...")

@app.route("/status", methods=["GET"])
def status():
	return "a-ok"

@app.route("/process", methods=["POST"])
def process():
	t0 = time.time()
	results = processFilePaths(request.json["filePaths"])
	print("processFilePaths --- %s seconds ---" % (time.time() - t0))
	return jsonify(results)

print("nsfwServer: Server running on port: " + str(cfg.web_port))
app.run(host="127.0.0.1", port=cfg.web_port, threaded=False)




