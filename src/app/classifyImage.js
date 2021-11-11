import {xu} from "xu";
import {cmdUtil, fileUtil} from "xutil";
import {classifyImage} from "../../tensor/tensorUtil.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "classifyImage",
	version : "1.0.0",
	desc    : "Classify an image with tensor",
	opts    :
	{
		model    : {desc : "Which tensor model to use", defaultValue : "garbage"},
		json     : {desc : "Output JSON"},
		jsonFile : {desc : "If set, will output the result JSON to the given filePath", hasValue : true}
	},
	args :
	[
		{argid : "inputFilePath", desc : "Path to an image to classify", required : true}
	]});

const r = await classifyImage(argv.inputFilePath, argv.model);
if(argv.jsonFile)
	await fileUtil.writeFile(argv.jsonFile, JSON.stringify(r));
console.log(argv.json ? JSON.stringify(r) : r);
