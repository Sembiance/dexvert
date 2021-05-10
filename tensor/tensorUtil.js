"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
	runUtil = require("@sembiance/xutil").run,
	httpUtil = require("@sembiance/xutil").http,
	C = require("../src/C.js"),
	tiptoe = require("tiptoe");

const TENSOR_DIM = [224, 224];
const RUN_OPTIONS = {silent : true, timeout : XU.MINUTE*2};

exports.PREPARE_METHODS = ["centerCrop", "scaleDown", "smartCrop"];

exports.prepareImage = function prepareImage({inPath, outPath, method="centerCrop"}, cb)
{
	if(!exports.PREPARE_METHODS.includes(method))
		return cb(new Error(`Invalid tensorUtil.prepareImage method: ${method}`));

	tiptoe(
		function cropAsInstructed()
		{
			if(method==="smartCrop")
				runUtil.run("smartcrop", [inPath, outPath, TENSOR_DIM.join("x")], RUN_OPTIONS, this);
			else if(method==="scaleDown")
				runUtil.run("convert", [inPath, "-background", "transparent", "-gravity", "center", "-resize", `${TENSOR_DIM.join("x")}>`, "-extent", TENSOR_DIM.join("x"), "+repage", outPath], RUN_OPTIONS, this);
			else if(method==="centerCrop")
				runUtil.run("convert", [inPath, "-background", "transparent", "-gravity", "center", "-crop", `${TENSOR_DIM.join("x")}+0+0`, "-extent", TENSOR_DIM.join("x"), "+repage", outPath], RUN_OPTIONS, this);
		},
		cb
	);
};

exports.classifyImage = function classifyImage(imagePath, modelName, cb)
{
	const METHODS = ["centerCrop", "scaleDown"];
	const tmpImagePaths = METHODS.map(v => fileUtil.generateTempFilePath(undefined, `_${v}.png`));

	function parseClassification(resultRaw)
	{
		let confidence = null;
		try
		{
			const result = JSON.parse(resultRaw.toString());
			if(result.error)
				return setImmediate(() => cb(new Error(result.error)));
			
			confidence = result.Confidences[0];
		}
		catch(err) {}

		return {confidence : confidence||0, raw : resultRaw.toString()};
	}

	const pngTrimmedPath = fileUtil.generateTempFilePath(undefined, ".png");

	tiptoe(
		function convertToPNG()
		{
			// If we end with .svg, assume it's an .svg
			// We do the funny cwd and leading ./ to handle files that start with dashes
			if(imagePath.endsWith(".svg"))
				runUtil.run("inkscape", ["--export-area-drawing", "-o", pngTrimmedPath, `./${path.basename(imagePath)}`], {...RUN_OPTIONS, cwd : path.dirname(imagePath)}, this);
			else
				runUtil.run("convert", [`./${path.basename(imagePath)}[0]`, pngTrimmedPath], {...RUN_OPTIONS, cwd : path.dirname(imagePath)}, this);	// We use [0] just in case the src image is an animation, so we just use the first frame
		},
		function trimImage()
		{
			runUtil.run("autocrop", [pngTrimmedPath], RUN_OPTIONS, this);
		},
		function performPreperation()
		{
			tmpImagePaths.parallelForEach((tmpImagePath, subcb, i) => exports.prepareImage({ inPath : pngTrimmedPath, outPath : tmpImagePath, method : METHODS[i]}, subcb), this);
		},
		function runClassifications()
		{
			tmpImagePaths.filterInPlace(tmpImagePath => fileUtil.existsSync(tmpImagePath));

			tmpImagePaths.parallelForEach((tmpImagePath, subcb) => httpUtil.post(`http://${C.TENSORSERV_HOST}:${C.TENSORSERV_PORT}/classify/${modelName}`, {imagePath : tmpImagePath}, {postAsJSON : true}, subcb), this);
		},
		function parseClassifications(resultsRaw)
		{
			this.parallel()(undefined, {confidence : resultsRaw.map(rawGP => parseClassification(rawGP).confidence).average(), raw : resultsRaw.map(v => v.toString())});
			tmpImagePaths.parallelForEach((tmpImagePath, subcb) => fileUtil.unlink(tmpImagePath, subcb), this.parallel());
			fileUtil.unlink(pngTrimmedPath, this.parallel());
		},
		cb
	);
};
