import {xu} from "xu";
import {cmdUtil} from "xutil";
import {preProcessPNG} from "../src/classifyUtil.js";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <inputFilePath> image and creates output images in <outputDirPath>",
	opts    :
	{
		model : {desc : "Which classification model to use", defaultValue : "garbage"}
	},
	args :
	[
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true},
		{argid : "inputFilePath", desc : "Image file to process", required : true, multiple : true}
	]});

for(const inputFilePath of argv.inputFilePath)
	await preProcessPNG(argv.model, inputFilePath, argv.outputDirPath);
