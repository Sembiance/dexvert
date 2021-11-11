import {xu} from "xu";
import {cmdUtil} from "xutil";
import {classifyImage} from "../tensorUtil.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "classifyImage",
	version : "1.0.0",
	desc    : "Classify an image with tensor",
	opts    :
	{
		model : {desc : "Which tensor model to use", defaultValue : "garbage"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "Path to an image to classify", required : true}
	]});

console.log(await classifyImage(argv.inputFilePath, argv.model));
