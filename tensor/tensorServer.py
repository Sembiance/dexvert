import os
import logging

from PIL import Image
from flask import Flask, request, jsonify
from TensorModel import TensorModel

app = Flask(__name__)

logging.getLogger('werkzeug').setLevel(logging.WARNING)

print("tensorServer: Loading model...")
modelGarbage = TensorModel(os.path.realpath(os.path.join(os.path.dirname(__file__), "garbage", "model")))

print("tensorServer: Defining flask routes...")

@app.route("/status", methods=["GET"])
def status():
	return jsonify(status="a-ok")

@app.route("/classify/garbage", methods=["POST"])
def classifyGarbage():
	image = Image.open(request.json["imagePath"])

	width, height = image.size
	if width != 224 or height != 224:
		return jsonify(error = "Invalid image dimensions " + str(width) + "x" + str(height) + ": " + request.json["imagePath"])

	if image.mode != "RGB":
		image = image.convert("RGB")

	#print("Classifying [garbage] image [" + request.json["imagePath"] + "] with dimensions " + str(width) + "x" + str(height))
	return jsonify(modelGarbage.predict(image))

print("tensorServer: Running flask server...")
app.run(host="0.0.0.0", port=17736, threaded=True)
