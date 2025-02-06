import {xu} from "xu";
import {cmdUtil, fileUtil} from "xutil";
import {XLog} from "xlog";
import {assert, writeAll} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const xlog = new XLog("info");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Converts <input> from DOOM Picture Format and outputs a .ppm",
	opts :
	{
		palette : {desc : "Path to the PLAYPAL palette file", hasValue : true, required : true}
	},
	args :
	[
		{argid : "inputFilePath", desc : "File path to convert", required : true},
		{argid : "outputFilePath", desc : "Output PPM file to write to", required : true}
	]});

if(!await fileUtil.exists(argv.palette))
	throw new Error(`Palette file not found: ${argv.palette}`);

// DOOM PIC format: https://doomwiki.org/wiki/Picture_format
const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});
const width = reader.uint16();
assert(width!==0, `Invalid width: ${width}`);
const height = reader.uint16();
assert(height!==0, `Invalid height: ${height}`);

reader.skip(4); // skip leftoffset & topoffset

const colOffsets = [];
for(let i=0;i<width;i++)
	colOffsets.push(reader.uint32());

// set default background color to black (technically the format spec says to use cyan or something, but files like 028.TITLEPIC seem to assume black)
const imageData = new Uint8Array(width*height*3);
for(let i=0;i<width*height;i++)
	imageData.set([0, 0, 0], i*3);

const paletteData = await fileUtil.readFileBytes(argv.palette, 768);

// Process each column
for(let col=0;col<width;col++)
{
	reader.setPOS(colOffsets[col]);
	while(true)
	{
		const rowStart = reader.uint8();
		if(rowStart===255)
			break;

		const pixelCount = reader.uint8();
		reader.skip(1); // skip dummy
		for(let j=0;j<pixelCount;j++)
		{
			const pixIdx = reader.uint8();
			const row = rowStart + j;
			if(row<height)
			{
				const idx = ((row*width)+col)*3;
				imageData[idx]     = paletteData[pixIdx*3];
				imageData[idx + 1] = paletteData[(pixIdx*3)+1];
				imageData[idx + 2] = paletteData[(pixIdx*3)+2];
			}
		}
		reader.skip(1); // skip dummy
	}
}

const encoder = new TextEncoder();
const outPPM = await Deno.open(argv.outputFilePath, {create : true, write : true, truncate : true});
await writeAll(outPPM, encoder.encode(`P6 ${width} ${height} 255\n`));
await writeAll(outPPM, imageData);
outPPM.close();
