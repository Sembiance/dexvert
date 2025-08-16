/* eslint-disable no-unused-vars */
import {xu} from "xu";
import {cmdUtil, fileUtil, runUtil} from "xutil";
import {assert, writeAll} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <input> as an jingTaoPicFormatBitmap file and converts to JPG outputFilePath",
	args :
	[
		{argid : "inputFilePath", desc : "jingTaoPicFormatBitmap to convert", required : true},
		{argid : "outputFilePath", desc : "Output JPG file to save as", required : true}
	]});

const outJPG = await Deno.open(argv.outputFilePath, {create : true, write : true, truncate : true});
await writeAll(outJPG, new Uint8Array([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01, 0x11, 0x00, 0x00, 0x01]));
await writeAll(outJPG, await Deno.readFile(argv.inputFilePath));
outJPG.close();
