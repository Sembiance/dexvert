import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil, fileUtil} from "xutil";
import {path} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Show the expected test data for a given file path",
	args :
	[
		{argid : "inputFilePath", desc : "Path of file to get test data about", required : true}
	]});

const xlog = new XLog();

const DATA_FILE_PATH = path.join(import.meta.dirname, "testExpected.json");
const testData = xu.parseJSON(await fileUtil.readTextFile(DATA_FILE_PATH), {});

const fileKey = path.relative(path.join(import.meta.dirname, "sample"), path.resolve(argv.inputFilePath));
xlog.info`${testData[fileKey]}`;
