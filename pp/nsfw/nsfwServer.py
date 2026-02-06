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

nsfwModel = make_open_nsfw_model(weights_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "weights", "open_nsfw_weights-0.1.0.h5"))

print("nsfwServer: Warming up...")
dummy = tf.zeros((1, 224, 224, 3))
nsfwModel.predict(dummy, verbose=0)

def processFilePaths(filePaths):
	results = []
	tensors = tf.convert_to_tensor([np.load(filePath + ".npy") for filePath in filePaths])
	predictions = nsfwModel.predict(tensors, batch_size=8, verbose=0)
	nsfwProbabilities: List[float] = predictions[:, 1].tolist()
	return [nsfwProbability*100 for nsfwProbability in nsfwProbabilities]

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
