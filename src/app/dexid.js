import {xu} from "xu";
import {cmdUtil} from "xutil";
import {identify} from "../identify.js";

const argv = cmdUtil.cmdInit({
	cmdid   : "dexid",
	version : "1.0.0",
	desc    : "Identifies one or more files",
	opts    :
	{
		verbose  : {desc : "Show additional info when identifying"},
		json     : {desc : "Output JSON"},
		jsonFile : {desc : "If set, will output the result JSON to the given filePath", hasValue : true}
	},
	args :
	[
		{argid : "inputFilePath", desc : "One or more file paths to identify", required : true, multiple : true}
	]});

for(const inputFilePath of Array.force(argv.inputFilePath))
{
	const identifications = await identify(inputFilePath, {verbose : argv.verbose});
	console.log({identifications});
}
