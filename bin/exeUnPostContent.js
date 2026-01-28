import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil} from "xutil";
import {UInt8ArrayReader} from "UInt8ArrayReader";
import {getEXEOverlayOffset} from "../src/dexUtil.js";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Tries to extract the tail end of an PE EXE file, so long as a specific ID string is found at the calculated offset",
	args :
	[
		{argid : "idstring", desc : "The string that must be found at the end of the file", required : true},
		{argid : "inputFilePath", desc : "DOS backup file to extract", required : true},
		{argid : "outputFilePath", desc : "Output file path to save to", required : true}
	]});

const xlog = new XLog(argv.logLevel);

const overlayOffset = await getEXEOverlayOffset(argv.inputFilePath);
if(!overlayOffset)
	Deno.exit(0);

const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});
reader.setPOS(overlayOffset);
if(reader.str(argv.idstring.length)!==argv.idstring)
	Deno.exit(xlog.error`No ${argv.idstring} string found at calculated offset ${overlayOffset}`);

reader.rewind(argv.idstring.length);
await reader.writeToDisk(reader.arr.length-overlayOffset, argv.outputFilePath);
