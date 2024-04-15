/* eslint-disable no-unused-vars */
import {xu} from "xu";
import {cmdUtil, fileUtil, runUtil} from "xutil";
import {assert} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <input> as an STEVE SND file and converts to wav outputFilePath",
	args :
	[
		{argid : "inputFilePath", desc : "STEVE SND file to extract", required : true},
		{argid : "outputFilePath", desc : "Output WAV file to save as", required : true}
	]});

// from: https://discmaster.textfiles.com/view/22622/cd3.iso/son/dos/playsn25.zip/source.zip/play.c
const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});
assert(reader.str(5)==="STEVE");
const version = reader.uint8();
assert(reader.str(1)==="H");
const sampleSize = reader.uint32();
assert(sampleSize<=(reader.remaining()-21));
reader.skip(19);
const frequency = reader.uint16();	// this value doesn't make sense, so we will just hardcod it below to 8900 which is what version 1 is hardcoded at

const tmpRawFilePath = await fileUtil.genTempPath(undefined, ".raw");
await reader.writeToDisk(sampleSize, tmpRawFilePath);
await runUtil.run("sox", ["-t", "raw", "-r", "8900", "-c", "1", "-b", "8", "-e", "unsigned", tmpRawFilePath, argv.outputFilePath]);
await fileUtil.unlink(tmpRawFilePath);
