/* eslint-disable no-bitwise */
import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil} from "xutil";
import {path} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Extracts icons from Apple 2 icon file <inputFilePath> and saves them as PPM files to <outputDirPath>",
	opts    :
	{
		logLevel : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: warn", defaultValue : "warn"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "Apple 2 icon file to extract", required : true},
		{argid : "outputDirPath", desc : "Output dir to save icons to", required : true}
	]});

// This code basically copied from: https://github.com/dmolony/DiskBrowser/blob/master/src/com/bytezone/diskbrowser/applefile/IconFile.java

const xlog = new XLog(argv.logLevel);

const br = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le", pos : 26});
const SCALE = 6;

const PALETTE =
[
	[0x00, 0x00, 0x00], // 0 black
	[0xDD, 0x00, 0x33], // 1 magenta
	[0x88, 0x55, 0x00], // 2 brown         (8)
	[0xFF, 0x66, 0x00], // 3 orange        (9)
	[0x00, 0x77, 0x22], // 4 dark green
	[0x55, 0x55, 0x55], // 5 grey1
	[0x11, 0xDD, 0x00], // 6 light green   (C)
	[0xFF, 0xFF, 0x00], // 7 yellow        (D)
	[0x00, 0x00, 0x99], // 8 dark blue     (2)
	[0xDD, 0x22, 0xDD], // 9 purple        (3)
	[0xAA, 0xAA, 0xAA], // A grey2
	[0xFF, 0x99, 0x88], // B pink
	[0x22, 0x22, 0xFF], // C med blue      (6)
	[0x66, 0xAA, 0xFF], // D light blue    (7)
	[0x44, 0xFF, 0x99], // E aqua
	[0xFF, 0xFF, 0xFF]	// F white
];

const te = new TextEncoder();

let iconNum=0;
while(!br.eof())
{
	const icon = br.sub(br.uint16()-2);
	if(icon.length()===0)
		break;

	xlog.debug`${"#".repeat(10)} ICON ${iconNum} ${"#".repeat(10)}`;

	const pathNameLength = icon.uint8();
	const pathName = icon.str(pathNameLength);
	xlog.debug`${{pathNameLength, pathName}}`;

	icon.setPOS(64);
	const dataNameLength = icon.uint8();
	const dataName = icon.str(dataNameLength);
	xlog.debug`${{dataNameLength, dataName}}`;

	icon.setPOS(80);
	const dataType = icon.uint16();
	const dataAux = icon.uint16();
	xlog.debug`${{dataType : dataType.toString(16), dataAux}}`;

	const iconType = icon.uint16();
	if(![0, 0x8000, 0xFFFF, 0x00FF].includes(iconType))	// 0x7FFF and 0x8001 exist out there but not currently supported. See: https://github.com/dmolony/DiskBrowser/blob/668ed719fac284fc4e4f86a2bdaa6220db8f2922/src/com/bytezone/diskbrowser/applefile/IconFile.java#L223
		Deno.exit(xlog.error`Invalid iconType: ${iconType.toString(16)}`);

	const iconSize = icon.uint16();
	const iconHeight = icon.uint16();
	const iconWidth = icon.uint16();
	if(iconHeight===0 || iconWidth===0)
		Deno.exit(xlog.error`Invalid icon size`);
	xlog.debug`${{iconType, iconSize, iconHeight, iconWidth}}`;
	
	const pixelData = icon.sub(iconSize);
	const maskData = icon.sub(iconSize);
	
	const ppmData = Array.from(te.encode(`P6\n${(iconWidth*6).toString()} ${(iconHeight*6).toString()}\n255\n`));
	const bytesPerRow = Math.floor(iconWidth/2);
	for(let y=0;y<iconHeight;y++)
	{
		const rowPixels = [];
		for(let x=0;x<bytesPerRow;x++)
		{
			const pixel = pixelData.uint8();
			const mask = maskData.uint8();
			const left = (pixel&0xF0)>>>4;
			const right = (pixel&0x0F);
			const maskLeft = (mask&0xF0)>>>4;
			const maskRight = (mask&0x0F);
			const colorIndexLeft = left&maskLeft;
			const colorIndexRight = right&maskRight;

			rowPixels.push(...Array(SCALE).fill(PALETTE[colorIndexLeft]).flat(), ...Array(SCALE).fill(PALETTE[colorIndexRight]).flat());
		}

		ppmData.push(...Array(SCALE).fill(rowPixels).flat());
	}

	await Deno.writeFile(path.join(argv.outputDirPath, `out_${iconNum.toString().padStart(2, "0")}.ppm`), Uint8Array.from(ppmData));

	iconNum++;
}
