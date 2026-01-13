import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil} from "xutil";
import {UInt8ArrayReader} from "UInt8ArrayReader";

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

// file format: http://fileformats.archiveteam.org/wiki/MS-DOS_EXE
const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});
if(reader.str(2)!=="MZ")
	Deno.exit(xlog.error`Invalid DOS EXE file header`);

reader.setPOS(0x3C);
const peHeaderOffset = reader.uint32();

reader.setPOS(peHeaderOffset);
if(reader.str(4)!=="PE\0\0")
	Deno.exit(xlog.error`Invalid PE header`);
reader.skip(2);

const numSections = reader.uint16();
reader.skip(12);

const sizeOfOptionalHeader = reader.uint16();
reader.skip(2);

reader.setPOS((peHeaderOffset+24+sizeOfOptionalHeader)+((numSections-1)*40)+16);
const extraStartOffset = reader.uint32() + reader.uint32();
reader.setPOS(extraStartOffset);

if(reader.str(4)!==argv.idstring)
	Deno.exit(xlog.error`No ${argv.idstring} string found at calculated offset ${extraStartOffset}`);

reader.rewind(4);
await reader.writeToDisk(reader.arr.length-extraStartOffset, argv.outputFilePath);
