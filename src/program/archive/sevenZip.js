/*
import {Program} from "../../Program.js";

export class sevenZip extends Program
{
	website = "http://p7zip.sourceforge.net/";
	package = "app-arch/p7zip";
	flags = {"7zRSRCOnly":"Only care about the files contained within the output .rsrc folder for things like DLL/EXE extraction","7zSingleFile":"Likely just a single output result, so rename it to the name of the original input file","7zType":"What archive type to process as"};
}
*/

/*
"use strict";
/* eslint-disable no-bitwise */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	{BUFReader} = require("@sembiance/bufreader"),
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	path = require("path");

exports.meta =
{
	website        : "http://p7zip.sourceforge.net/",
	package  : "app-arch/p7zip",
	flags :
	{
		"7zRSRCOnly"   : "Only care about the files contained within the output .rsrc folder for things like DLL/EXE extraction",
		"7zSingleFile" : "Likely just a single output result, so rename it to the name of the original input file",
		"7zType"       : "What archive type to process as"
	}
};

exports.bin = () => "7z";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) =>
{
	const args = ["x", "-y"];
	r.outPath = outPath;

	if(r.flags["7zType"])
		args.push(`-t${r.flags["7zType"]}`);

	if(r.flags["7zRSRCOnly"])
	{
		r.tmpOutPath = fileUtil.generateTempFilePath(state.cwd, "7zRSRCOnly");
		fs.mkdirSync(r.tmpOutPath);
	}

	args.push(`-o${r.tmpOutPath || r.outPath}`, inPath);

	return args;
};

function getBMPInfo(bmpBuffer)
{
	// This code copied from: https://github.com/jsummers/deark/blob/master/src/fmtutil.c#L42
	if(bmpBuffer.length<16)
		return null;

	const br = new BUFReader(bmpBuffer, {endianness : "le"});
	const info = {headerSize : br.uint32()};
	
	// If it's a PNG formatted cursor, ignore it
	if(info.headerSize===0x474E5089)
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
		info.numColors = 16777216;
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
		info.totalSize = bmpBuffer.length;
	}

	if(info.width>255)
		info.width = 0;
	if(info.height>255)
		info.height = 0;
	if(info.numColors>255)
		info.numColors = 0;

	return info;
}

function fixCursor(cursorFilePath, cb)
{
	tiptoe(
		function loadCursorFile()
		{
			fs.readFile(cursorFilePath, this);
		},
		function writeNewCursorFile(cursorRawBuffer)
		{
			const info = getBMPInfo(cursorRawBuffer.subarray(4));
			if(!info)
				return this();

			// This code copied from: https://github.com/jsummers/deark/blob/master/modules/exe.c#L695
			const curBuf = Buffer.alloc(info.totalSize+22);
			curBuf.writeUInt16LE(0, 0);	// Reserved
			curBuf.writeUInt16LE(2, 2);	// Resource ID
			curBuf.writeUInt16LE(1, 4);	// # of cursors
			curBuf.writeUInt8(info.width, 6);
			curBuf.writeUInt8(info.height, 7);
			curBuf.writeUInt8(info.numColors, 8);
			curBuf.writeUInt8(0, 9);
			curBuf.writeUInt16LE(cursorRawBuffer.readUInt16LE(0), 10);	// Hotspot X
			curBuf.writeUInt16LE(cursorRawBuffer.readUInt16LE(2), 12);	// Hotspot Y
			curBuf.writeUInt32LE(info.totalSize, 14);	// Cursor Size
			curBuf.writeUInt32LE(6+16, 18);	// Cursor file offset
			cursorRawBuffer.copy(curBuf, 22, 4, 4+info.totalSize);

			if(cursorFilePath.toLowerCase().endsWith(".cur"))
			{
				fs.writeFile(cursorFilePath, curBuf, this);
			}
			else
			{
				fs.writeFile(`${cursorFilePath}.cur`, curBuf, this.parallel());
				fileUtil.unlink(cursorFilePath, this.parallel());
			}
		},
		cb
	);
}

exports.post = (state, p, r, cb) =>
{
	if(r.flags["7zSingleFile"])
		return p.util.file.move(path.join(state.output.absolute, "in"), path.join(state.output.absolute, `${state.input.name}`))(state, p, cb);
	
	if(r.flags["7zRSRCOnly"])
	{
		const STRIP_FILENAMES = ["version.txt", "string.txt"];
		tiptoe(
			function findFiles()
			{
				// 7z extracts things like DIALOGs, but it's not in a format I can really do anything with, so let's just get rid of it
				fileUtil.glob(r.tmpOutPath, "**/DIALOG/", this.parallel());
				fileUtil.glob(r.tmpOutPath, "**/CURSOR/*", {nodir : true}, this.parallel());
			},
			function processFiles(unusefulPaths, cursorFilePaths)
			{
				(unusefulPaths || []).parallelForEach((unusefulPath, subcb) => p.util.file.unlink(unusefulPath)(state, p, subcb), this.parallel());

				// The cursor files extracted by 7z are RAW bitmap data and are missing their header. So we read the bitmap data and create the proper CUR header
				(cursorFilePaths || []).parallelForEach(fixCursor, this.parallel());
			},
			function moveRSRCFiles()
			{
				p.util.file.moveAllFiles(path.join(r.tmpOutPath, ".rsrc"), state.output.absolute)(state, p, this);
			},
			function stripNullBytes()
			{
				// Some output txt files have zero bytes every other byte, let's strip those out
				STRIP_FILENAMES.parallelForEach((filename, subcb) =>
				{
					const filePath = path.join(state.output.absolute, filename);
					if(fileUtil.existsSync(filePath))
						runUtil.run(path.join(__dirname, "..", "..", "..", "transform", "stripGarbage", "stripGarbage"), ["--null", filePath, `${filePath}-stripped`], runUtil.SILENT, subcb);
					else
						setImmediate(subcb);
				}, this);
			},
			function removeNonStrippedFiles()
			{
				STRIP_FILENAMES.parallelForEach((filename, subcb) =>
				{
					const filePath = path.join(state.output.absolute, filename);
					if(fileUtil.existsSync(filePath))
						fs.rename(`${filePath}-stripped`, filePath, subcb);
					else
						setImmediate(subcb);
				}, this);
			},
			function removeTmpOutPath()
			{
				fileUtil.unlink(r.tmpOutPath, this);
			},
			cb
		);
	}
	else
	{
		setImmediate(cb);
	}
};
*/
