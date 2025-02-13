import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil, fileUtil} from "xutil";
import {path} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <input> as a Palm MIDI ringtone file and extracts the MIDI files into dir <outputDirPath>",
	opts    :
	{
		logLevel : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: warn", defaultValue : "info"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "MIDI ringtone file to extract", required : true},
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true}
	]});

const xlog = new XLog(argv.logLevel);

// inspired by code: https://github.com/wackypack/mtex/blob/master/extract_midi_pdb.py
const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});

if(reader.skipUntil("PMrc")===false)
	Deno.exit(0);

const headerLength = reader.uint16();
const name = reader.str(headerLength-7).trimChars("\0");
reader.skip(1);

const outputFilePath = path.join(argv.outputDirPath, `${name.replaceAll("..", "--").replaceAll("/", "∕")}.mid`);
while(1)
{
	const midiData = reader.skipUntil([0xFF, 0x2F, 0x00]);
	if(midiData===false)
	{
		await fileUtil.unlink(outputFilePath, {recursive : true});
		Deno.exit(0);
	}

	await midiData.writeToDisk(midiData.length(), outputFilePath, {create : true, append : true});
	if(reader.remaining()<4 || reader.str(4)!=="MTrk")
		break;

	reader.rewind(4);
}
