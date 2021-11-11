import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
os.environ["FLASK_ENV"] = "production"

import tensorflow as tf
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

import json
import numpy as np
from PIL import Image

class TensorModel(object):
	def __init__(self, model_path):
		config = ConfigProto()
		config.gpu_options.allow_growth = True
		session = InteractiveSession(config=config)

		# The signature json file shows us the model inputs and outputs, data types, shapes and names
		with open(os.path.join(model_path, "signature.json"), "r") as f:
			self.signature = json.load(f)
		self.inputs = self.signature.get("inputs")
		self.outputs = self.signature.get("outputs")
		self.session = tf.compat.v1.Session(graph=tf.Graph())
		tf.compat.v1.saved_model.loader.load(sess=self.session, tags=self.signature.get("tags"), export_dir=model_path)

	def predict(self, image: Image.Image):
		# Make 0-1 float instead of 0-255 int (that PIL Image loads by default)
		image = np.asarray(image) / 255.0

		# Create the feed dictionary that is the input to the model, add our image to the dict (comes from our signature.json file)
		feed_dict = {self.inputs["Image"]["name"]: [image]}

		# List the outputs we want from the model -- these come from our signature.json file
		# Since we are using dicts that could have different orders, make tuples of (key, name) to keep track for putting the results back together into a dict
		fetches = [(key, output["name"]) for key, output in self.outputs.items()]

		# Run the model! There will be as many outputs from session.run as you have in the fetches list
		outputs = self.session.run(fetches=[name for _, name in fetches], feed_dict=feed_dict)

		results = {}
		# We ran on a batch of size 1. Index out the items from the returned numpy arrays
		for i, (key, _) in enumerate(fetches):
			val = outputs[i].tolist()[0]
			if isinstance(val, bytes):
				val = val.decode()
			results[key] = val
		return results

	def __del__(self):
		if self.session is not None:
			self.session.close()
			self.session = None
