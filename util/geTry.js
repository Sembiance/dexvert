import {xu} from "xu";
import {C} from "../src/C.js";
import {fileUtil, cmdUtil} from "xutil";
import {path} from "std";
import {XLog} from "xlog";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Attempts to extract a file with GameExtractorServer",
	args :
	[
		{argid : "codes", desc : "Codes to try, can be comma delimited", required : true},
		{argid : "inputFilePath", desc : "Input file to scan", required : true}
	]});

const outputDirPath = await fileUtil.genTempPath();

const args = {inputFilePath : path.resolve(argv.inputFilePath), outputDirPath};
if(argv.codes!=="NONE")
	args.codes = argv.codes.toString().split(",");

const result = await xu.fetch(`http://${C.GAMEEXTRACTOR_HOST}:${C.GAMEEXTRACTOR_PORT}/extract`, {json : args, asJSON : true});

xlog.info`${result};`;
xlog.info`outputDirPath: ${outputDirPath}`;
