import {xu} from "xu";
import {C} from "../src/C.js";
import {fileUtil, cmdUtil, runUtil} from "xutil";
import {path} from "std";
import {XLog} from "xlog";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Attempts to extract a file with vgmstreamServer",
	args :
	[
		{argid : "types", desc : "Types to try, can be comma delimited (enter NONE to try all)", required : true},
		{argid : "inputFilePath", desc : "Input file to scan", required : true}
	]});

const outputDirPath = await fileUtil.genTempPath(C.DEXVERT_TMP_DIR);

const args = {inputFilePath : path.resolve(argv.inputFilePath), outputDirPath, formatid : argv.types};
const result = await xu.fetch(`http://${C.VGMSTREAM_HOST}:${C.VGMSTREAM_PORT}/convert`, {json : args, asJSON : true});

xlog.info`${result};`;
await runUtil.run("tree", [outputDirPath], {liveOutput : true});
xlog.info`outputDirPath: ${outputDirPath}`;
