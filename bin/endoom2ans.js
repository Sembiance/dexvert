import {xu} from "xu";
import {cmdUtil, encodeUtil, printUtil} from "xutil";
import {XLog} from "xlog";
import {writeAll} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const xlog = new XLog("info");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Converts <input> from Doom 'endoom' format to .ans",
	opts :
	{
		debug : {desc : "Debug output"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "ENDOOM file path to convert", required : true},
		{argid : "outputFilePath", desc : "Output ANS file to write to", required : true}
	]});

// Format: https://doomwiki.org/wiki/ENDOOM

const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});
const charsRaw = [];
const colorsRaw = [];
while(reader.remaining())
{
	charsRaw.push(reader.uint8());
	colorsRaw.push(reader.uint8());
}

const FG_TO_ANSI = [30, 34, 32, 36, 31, 35, 33, 37, 90, 94, 92, 96, 91, 95, 93, 97];
const BG_TO_ANSI = [40, 44, 42, 46, 41, 45, 43, 47];

const outANS = await Deno.open(argv.outputFilePath, {create : true, write : true, truncate : true});
const chars = (await encodeUtil.decode(new Uint8Array(charsRaw), "CP437")).split("");
const encoder = new TextEncoder();
for(let y=0;y<25;y++)
{
	for(let x=0;x<80;x++)
	{
		const charRaw = charsRaw.shift();
		const char = chars.shift();
		const colorRaw = colorsRaw.shift();
		const fg = colorRaw.bitsToNum(4, 0);
		const bg = colorRaw.bitsToNum(3, 4);
		const blink = colorRaw.getBit(7);
		if(blink)
			xlog.info`blink: ${blink}`;
		const escapeCode = `\x1B[${BG_TO_ANSI[bg]};${FG_TO_ANSI[fg]}m`;	// eslint-disable-line unicorn/no-hex-escape
		await writeAll(outANS, new Uint8Array([...encoder.encode(escapeCode), charRaw, ...encoder.encode(xu.c.reset)]));
		if(argv.debug)
			printUtil.stdoutWrite(`${escapeCode}${char}${xu.c.reset}`);
	}
	if(argv.debug)
		printUtil.stdoutWrite("\n");
}

outANS.close();
