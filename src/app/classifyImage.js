import {xu} from "xu";
import {cmdUtil} from "xutil";
import {classifyImage} from "../classifyUtil.js";
import {initRegistry} from "../dexUtil.js";
import {XLog} from "xlog";

const argv = cmdUtil.cmdInit({
	cmdid   : "classifyImage",
	version : "1.0.0",
	desc    : "Classify an image",
	opts    :
	{
		model : {desc : "Which classification model to use", defaultValue : "garbage"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "Path to an image to classify", required : true, multiple : true}
	]});

const xlog = new XLog("warn");
await initRegistry(xlog);

for(const inputFilePath of argv.inputFilePath)
{
	const garbageScore = await classifyImage(inputFilePath, argv.model, xlog);
	console.log(`${garbageScore>0}\t${garbageScore.toFixed(10)}\t${inputFilePath}`);
}
