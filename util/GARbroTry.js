import {xu} from "xu";
import {C} from "../src/C.js";
import {fileUtil, cmdUtil} from "xutil";
import {path} from "std";
import {XLog} from "xlog";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Attempts to extract a file with GARbroserver",
	args :
	[
		{argid : "types", desc : "Codes to try, can be comma delimited", required : true},
		{argid : "inputFilePath", desc : "Input file to scan", required : true}
	]});

const outputDirPath = await fileUtil.genTempPath();

const args = {inputFilePath : path.resolve(argv.inputFilePath), outputDirPath};
args.formatId = argv.types.toString();

const result = await xu.fetch(`http://${C.GARBRO_HOST}:${C.GARBRO_PORT}/extract`, {json : args, asJSON : true});

xlog.info`${result};`;
xlog.info`outputDirPath: ${outputDirPath}`;
