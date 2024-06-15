import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil} from "xutil";
import {path, assert} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <input> as a DOS backup file and restores it with full path into dir <outputDirPath>",
	opts    :
	{
		logLevel : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: warn", defaultValue : "info"},
		backupVersion : {desc : "What DOS backup version to support", hasValue : true, defaultValue : "2.0-3.2"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "DOS backup file to extract", required : true},
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true}
	]});

const xlog = new XLog(argv.logLevel);

if(argv.backupVersion!=="2.0-3.2")
	Deno.exit(xlog.error`Only DOS backup version 2.0-3.2 is supported right now`);

// file format: https://www.ibiblio.org/pub/micro/pc-stuff/freedos/files/dos/restore/brtecdoc.htm

const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});

assert(reader.uint8()===0xFF, `Only complete files supported right now`);
assert(reader.uint16()===1, `Only complete files supported right now`);

reader.skip(2);

const subPathOriginal = reader.sub(78).strNullTerminated();
let subPath = subPathOriginal.replaceAll("\\", "/");
if(subPath.startsWith("/"))
	subPath = subPath.slice(1);

assert(reader.uint8()===subPathOriginal.length+1, `Invalid subpath length`);

reader.skip(44);

const outputDirPath = path.resolve(argv.outputDirPath);
const outputFilePath = path.resolve(path.join(outputDirPath, subPath));
assert(path.dirname(outputFilePath).startsWith(outputDirPath), `Invalid subpath ${subPathOriginal} in backup file ${argv.inputFilePath}`);

await Deno.mkdir(path.dirname(outputFilePath), {recursive : true});
await reader.writeToDisk(reader.remaining(), outputFilePath);
