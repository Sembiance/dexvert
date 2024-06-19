/* eslint-disable no-bitwise */
import {xu} from "xu";
import {cmdUtil} from "xutil";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Fixes cursor files extracted by 7z to have a proper header",
	args :
	[
		{argid : "inputFilePath", desc : "Input bad 7z CUR file to parse", required : true},
		{argid : "outputFilePath", desc : "Output file to write to", required : true}
	]});

function getBMPInfo(bmpArray)
{
	// This code copied from: https://github.com/jsummers/deark/blob/master/src/fmtutil.c#L42
	if(bmpArray.length<16)
		return null;

	const br = new UInt8ArrayReader(bmpArray, {endianness : "le", pos : 4});
	const info = {headerSize : br.uint32()};
	
	// If it's a PNG formatted cursor, ignore it
	if(info.headerSize===0x47_4E_50_89)
		return null;
	
	if(info.headerSize===12)
	{
		info.bytesPerPalEntry = 3;
		info.width = br.uint16();
		info.height = br.uint16();
		info.bitCount = br.uint16();
	}
	else if(info.headerSize>=16 && info.headerSize<=124)
	{
		info.bytesPerPalEntry = 4;
		info.width = br.uint32();
		info.height = br.int32();

		if(info.height<0)
		{
			info.isTopDown = 1;
			info.height = -info.height;
		}

		br.skip(2);
		info.bitCount = br.uint16();

		if(info.headerSize>=20)
			info.compressionField = br.uint32();
		if(info.headerSize>=24)
		{
			br.setPOS(20);
			info.sizeImageField = br.uint32();
		}

		if(info.headerSize>=36)
		{
			br.setPOS(32);
			info.palEntries = br.uint32();
		}
	}
	else
	{
		return null;
	}

	info.height/=2;

	if(info.bitCount>=1 && info.bitCount<=8)
	{
		if(info.palEntries===0)
			info.palEntries = 1<<info.bitCount;
		
		info.numColors = 1<<info.bitCount;
	}
	else
	{
		info.numColors = 16_777_216;
	}

	if(info.palEntries>256 && info.bitCount>8)
		info.palEntries = 0;
	
	info.palBytes = info.bytesPerPalEntry*info.palEntries;
	info.sizeOfHeaderAndPal = info.headerSize + info.palBytes;
	
	if(info.compressionField===0)
	{
		info.rowSpan = ((info.bitCount*info.width)/32)*4;
		info.foregroundSize = info.rowSpan*info.height;
		info.maskRowSpan = (info.width/32)*4;
		info.maskSize = info.maskRowSpan*info.height;
		info.totalSize = info.sizeOfHeaderAndPal + info.foregroundSize + info.maskSize;
	}
	else
	{
		info.totalSize = bmpArray.length;
	}

	if(info.width>255)
		info.width = 0;
	if(info.height>255)
		info.height = 0;
	if(info.numColors>255)
		info.numColors = 0;

	return info;
}

const curRaw = await Deno.readFile(argv.inputFilePath);
const info = getBMPInfo(curRaw);
if(!info)
	Deno.exit(0);

// This code copied from: https://github.com/jsummers/deark/blob/master/modules/exe.c#L695
const curBuf = new Uint8Array(info.totalSize+22);
curBuf.setUInt16LE(0, 0);	// Reserved
curBuf.setUInt16LE(2, 2);	// Resource ID
curBuf.setUInt16LE(4, 1);	// # of cursors
curBuf.setUInt8(6, info.width);
curBuf.setUInt8(7, info.height);
curBuf.setUInt8(8, info.numColors);
curBuf.setUInt8(9, 0);
curBuf.setUInt16LE(10, curRaw.getUInt16LE(0));	// Hotspot X
curBuf.setUInt16LE(12, curRaw.getUInt16LE(2));	// Hotspot Y
curBuf.setUInt32LE(14, info.totalSize);	// Cursor Size
curBuf.setUInt32LE(18, 6+16);	// Cursor file offset

curRaw.copy(curBuf, 22, 4, 4+info.totalSize);

await Deno.writeFile(argv.outputFilePath, curBuf);
