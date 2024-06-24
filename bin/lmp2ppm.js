import {xu} from "xu";
import {cmdUtil, fileUtil} from "xutil";
import {XLog} from "xlog";
import {assert, writeAll} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const xlog = new XLog("info");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Converts <input> from quake .lmp format and outputs a .ppm",
	opts :
	{
		palette : {desc : "Path to the palette.lmp file", hasValue : true, required : true}
	},
	args :
	[
		{argid : "inputFilePath", desc : "2D .lmp file path to convert", required : true},
		{argid : "outputFilePath", desc : "Output PPM file to write to", required : true}
	]});

if(!await fileUtil.exists(argv.palette))
	throw new Error(`Palette file not found: ${argv.palette}`);

//         lmp format: https://quakewiki.org/wiki/.lmp
// palette.lmp format: https://quakewiki.org/wiki/Quake_palette#palette.lmp
const paletteReader = new UInt8ArrayReader(await Deno.readFile(argv.palette), {endianness : "le"});
const palette = [];
while(palette.length<256)
	palette.push([paletteReader.uint8(), paletteReader.uint8(), paletteReader.uint8()]);

const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});
const width = reader.uint32();
assert(width!==0, `Invalid width: ${width}`);
const height = reader.uint32();
assert(height!==0, `Invalid height: ${height}`);

assert(width*height===reader.remaining(), `Invalid width/height`);

const encoder = new TextEncoder();

const outPPM = await Deno.open(argv.outputFilePath, {create : true, write : true, truncate : true});
await writeAll(outPPM, encoder.encode(`P6 ${width} ${height} 255\n`));
for(let y=0;y<height;y++)
{
	for(let x=0;x<width;x++)
		await writeAll(outPPM, new Uint8Array(palette[reader.uint8()]));
}
outPPM.close();
