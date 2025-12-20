import {xu} from "xu";
import {cmdUtil} from "xutil";
import {path} from "std";
import {XLog} from "xlog";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	desc    : "Processes <input> as a self-extracting InstallShield archive and extracts out it's installer files into <outputDirPath>",
	args :
	[
		{argid : "inputFilePath", desc : "File path to extract", required : true},
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true}
	]});

const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});
const MAGIC = [0x13, 0x5D, 0x65, 0x8C, 0x3A, 0x01, 0x02, 0x00];

let fileCount = 0;
while(reader.remaining())
{
	const headerData = reader.skipUntil(MAGIC);
	if(!headerData)
		break;

	reader.rewind(MAGIC.length + 4);
	await reader.writeToDisk(reader.uint32(), path.join(argv.outputDirPath, `out${(fileCount++).toString().padStart(3, "0")}.z`));
}
