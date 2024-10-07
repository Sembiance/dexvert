import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil} from "xutil";
import {path, assertStrictEquals} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Extracts files from a FrontPage Theme-Pack",
	opts    :
	{
		logLevel : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: warn", defaultValue : "warn"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "ELM theme file to extract from", required : true},
		{argid : "outputDirPath", desc : "Output dir to save files to", required : true}
	]});

const xlog = new XLog(argv.logLevel);

const br = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});

br.strTerminated(0x0A);	// version number
const numImages = +br.strTerminated(0x0A);
const files = [];
for(let i=0;i<numImages;i++)
{
	const [name, size] = br.strTerminated(0x0A).split(",");
	files.push({name, size : +size});
}

for(const {name, size} of files)
{
	assertStrictEquals(br.str(14), "<==MS-Theme==>");
	await Deno.writeFile(path.join(argv.outputDirPath, name), br.raw(size));
}

assertStrictEquals(br.remaining(), 0);
