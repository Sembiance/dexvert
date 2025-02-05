#!/usr/bin/env python3
import os, sys, importlib.util

def main():
	if len(sys.argv) < 4:
		print("Usage: {} <pluginFile> <resourceFile> <outDirPath>".format(sys.argv[0]))
		sys.exit(1)
	pluginFile = f"plugins/g_{sys.argv[1]}.py"
	resourceFile = sys.argv[2]
	outDirPath = sys.argv[3]
	os.makedirs(outDirPath, exist_ok=True)

	spec = importlib.util.spec_from_file_location("pluginMod", pluginFile)
	pluginMod = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(pluginMod)
	if not hasattr(pluginMod, "Game_Res"):
		print("Plugin does not define Game_Res")
		sys.exit(1)
	resObj = pluginMod.Game_Res(None)

	imagesList, soundList = [], []
	if hasattr(resObj, "open_data"):
		resObj.open_data(resourceFile)
		if not resObj.data:
			print("No resource data found.")
			sys.exit(0)
		for dataRes in resObj.data:
			resObj.unpack(dataRes)
			imagesList.extend(resObj.images)
			if resObj.sound:
				soundList.append(resObj.sound)
	else:
		fSize = os.path.getsize(resourceFile)
		ext = resourceFile.split(".")[-1].lower()
		dataRes = [resourceFile, None, fSize, ext]
		resObj.unpack(dataRes)
		imagesList = resObj.images
		if resObj.sound:
			soundList.append(resObj.sound)

	for i, img in enumerate(imagesList):
		path = os.path.join(outDirPath, f"{i:05d}.png")
		img.save(path)
		print("Saved", path)
	for i, snd in enumerate(soundList):
		path = os.path.join(outDirPath, f"{i:05d}.wav")
		with open(path, "wb") as f:
			f.write(snd.getvalue())
		print("Saved", path)

if __name__ == "__main__":
	main()
