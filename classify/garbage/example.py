
# ONNX for image classification model

import onnxruntime as ort
import numpy
from PIL import Image

ort_sess = ort.InferenceSession("model.onnx", providers=["CPUExecutionProvider"])
classes = [ "garbage" ,  "notGarbage" , ]

img = Image.open("image.jpg").convert("RGB")
img = img.resize((300, 300 * img.size[1] // img.size[0]))
inp_numpy = numpy.array(img)[None].astype("float32")


class_scores = ort_sess.run(None, {"input": inp_numpy})[0][0]



print("")
print("class_scores", class_scores)
print("Class : ", classes[class_scores.argmax()])

