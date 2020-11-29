"use strict";
/* eslint-disable node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	httpUtil = require("@sembiance/xutil").http,
	C = require("../lib/C.js"),
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe");

const TENSOR_DIM = [224, 224];
const SMART_CROP_COLOR_THRESHOLD = 2;

exports.prepareImage = function prepareImage(inImagePath, outImagePath, cb)
{
	const tmpImagePath = fileUtil.generateTempFilePath("/mnt/ram/tmp", path.extname(outImagePath));

	tiptoe(
		function cpToTmp()
		{
			fs.copyFile(inImagePath, tmpImagePath, this);
		},
		function autoCropImage()
		{
			runUtil.run("autocrop", [tmpImagePath], runUtil.SILENT, this);
		},
		function getDim()
		{
			runUtil.run("identify", ["-format", "%wx%h", tmpImagePath], runUtil.SILENT, this);
		},
		function extentOrCrop(dimRaw)
		{
			// If we are smaller than TENSOR_DIM then we just create an image of those dimensions and center our src on it
			const dim = dimRaw.trim().split("x").map(v => +v);
			if(dim[0]<TENSOR_DIM[0] && dim[1]<TENSOR_DIM[1])
				return runUtil.run("convert", [tmpImagePath, "-background", "transparent", "-gravity", "center", "-extent", TENSOR_DIM.join("x"), outImagePath], runUtil.SILENT, () => this.jump(-1)), undefined;
			
			// Otherwise let's crop to TENSOR_DIM at the center of the image
			runUtil.run("convert", [tmpImagePath, "-background", "transparent", "-gravity", "center", "-crop", `${TENSOR_DIM.join("x")}+0+0`, "-extent", TENSOR_DIM.join("x"), outImagePath], runUtil.SILENT, this);
		},
		function getColorCount()
		{
			// Now let's measure how many colors our cropped image has, because if it's too boring we'll need to crop more smartly
			runUtil.run("identify", ["-format", "%k", outImagePath], runUtil.SILENT, this);
		},
		function smartCropIfBoring(colorCountRaw)
		{
			const colorCount = +colorCountRaw || 0;
			if(!colorCount || colorCount>=SMART_CROP_COLOR_THRESHOLD)
				return this();

			// smartcrop finds the most interesting part of the image by using edge detection and crops to that
			// It's pretty slow though, so it's not worth doing for every image, but rather only if we get a boring image
			runUtil.run("smartcrop", [tmpImagePath, outImagePath, TENSOR_DIM.join("x")], runUtil.SILENT, this);
		},
		function cleanup()
		{
			fileUtil.unlink(tmpImagePath, this);
		},
		cb
	);
};

exports.classifyImage = function classifyImage(imagePath, modelName, cb)
{
	const tmpImagePath = fileUtil.generateTempFilePath("/mnt/ram/tmp", path.extname(imagePath));

	tiptoe(
		function prepareToTmp()
		{
			exports.prepareImage(imagePath, tmpImagePath, this);
		},
		function runClassification()
		{
			httpUtil.post(`http://${C.TENSORSERV_HOST}:${C.TENSORSERV_PORT}/classify/${modelName}`, {imagePath : tmpImagePath}, {postAsJSON : true}, this);
		},
		function parseClassification(gpRaw)
		{
			if(gpRaw)
			{
				let gp = null;
				try
				{
					gp = JSON.parse(gpRaw.toString()).Confidences[0];
				}
				catch(err) {}

				this.data.results = [gp, gp!==null ? gp.noExponents() : null, gpRaw.toString()];
			}

			fileUtil.unlink(tmpImagePath, this);
		},
		function returnResults()
		{
			this(undefined, this.data.results);
		},
		cb
	);
};
