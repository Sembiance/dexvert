import {xu} from "xu";
import {cmdUtil} from "xutil";
import {preProcessPNG} from "../src/tensorUtil.js";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <inputFilePath> image and creates output images in <outputDirPath>",
	args :
	[
		{argid : "inputFilePath", desc : "Image file to process", required : true},
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true}
	]});

await preProcessPNG(argv.inputFilePath, argv.outputDirPath);
