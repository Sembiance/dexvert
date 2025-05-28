import os
import logging

from PIL import Image
from flask import Flask, request, jsonify
import onnxruntime as ort
import numpy

app = Flask(__name__)

logging.getLogger('werkzeug').setLevel(logging.WARNING)

print("classifyServer: Loading models...")
ort_sess = ort.InferenceSession(os.path.realpath(os.path.join(os.path.dirname(__file__), "garbage", "model.onnx")), providers=["CPUExecutionProvider"])

print("classifyServer: Defining flask routes...")

@app.route("/status", methods=["GET"])
def status():
	return jsonify(status="a-ok")

@app.route("/classify/garbage", methods=["POST"])
def classifyGarbage():
	image = Image.open(request.json["imagePath"])

	width, height = image.size
	if(width != 300 or height != 300):
		return jsonify(error = "Invalid image dimensions " + str(width) + "x" + str(height) + ": " + request.json["imagePath"])

	if(image.mode != "RGB"):
		image = image.convert("RGB")

	#print("Classifying [garbage] image [" + request.json["imagePath"] + "] with dimensions " + str(width) + "x" + str(height))
	scores = ort_sess.run(None, {"input": numpy.array(image)[None].astype("float32")})[0][0]
	return jsonify(scores.tolist()[0]) if scores.argmax()==0 else jsonify(0)
	#return jsonify(scores.tolist())

print("classifyServer: Running flask server...")
app.run(host="127.0.0.1", port=17736, threaded=True)
