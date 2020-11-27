import os

from PIL import Image
from flask import Flask, request, jsonify
from TensorModel import TensorModel

app = Flask(__name__)

modelGarbage = TensorModel(os.path.realpath(os.path.join(os.path.dirname(__file__), "garbage", "model")))

@app.route("/status", methods=["GET"])
def status():
	return jsonify(status="a-ok")

@app.route("/classify/garbage", methods=["POST"])
def classifyGarbage():
	image = Image.open(request.json["imagePath"])
	if image.mode != "RGB":
		image = image.convert("RGB")
	return jsonify(modelGarbage.predict(image))

app.run(host="127.0.0.1", port=17736)
