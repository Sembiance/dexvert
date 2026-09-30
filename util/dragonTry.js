import {xu} from "xu";
import {C} from "../src/C.js";
import {fileUtil, cmdUtil} from "xutil";
import {path} from "std";
import {XLog} from "xlog";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Attempts to extract a file with dragonUnPACKer server",
	args :
	[
		{argid : "formatid", desc : "Which formatid to try", required : true},
		{argid : "inputFilePath", desc : "Input file to scan", required : true}
	]});

const outputDirPath = await fileUtil.genTempPath(C.DEXVERT_TMP_DIR);

const msg = {inputFilePath : path.resolve(argv.inputFilePath), outputDirPath, formatid : argv.formatid};

xlog.info`${msg}`;

const result = await xu.fetch(`http://${C.DRAGON_UNPACKER_HOST}:${C.DRAGON_UNPACKER_PORT}/extract`, {json : msg, asJSON : true});

xlog.info`${result};`;
xlog.info`outputDirPath: ${outputDirPath}`;
