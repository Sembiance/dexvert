/* eslint-disable no-bitwise */
import {xu} from "xu";
import {cmdUtil, fileUtil, encodeUtil, hashUtil, runUtil} from "xutil";
import {UInt8ArrayReader} from "UInt8ArrayReader";
import {XLog} from "xlog";
import {assert, path, writeAll} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Converts an AppleDouble file into a MacBinary 2 file. It will DELETE the file, and over-write the datafork file (non .rsrc/.adf) with the new macbinary file",
	opts :
	{
		region           : {desc : "Which region for filename encoding", hasValue : true, defaultValue : "roman"},
		originalFilePath : {desc : "The original file path that the AppleDouble file was created from, important to ensure we don't infinite loop the same MacBinary file over and over", hasValue : true, required : true}
	},
	args :
	[
		{argid : "inputFilePath", desc : "The AppleDouble file to convert (should end with .rsrc)", required : true}
	]});

// BIG THANKS to eientei for this script which helped a LOT: https://raw.githubusercontent.com/einstein95/py_scripts/main/deadf.py

const xlog = new XLog();

if(!await fileUtil.exists(argv.inputFilePath))
	Deno.exit(xlog.error`Input file does not exist: ${argv.inputFilePath}`);

const inputFilePath = path.resolve(argv.inputFilePath);
if(![".rsrc", ".adf"].some(v => inputFilePath.toLowerCase().endsWith(v)))
	Deno.exit(xlog.error`Only AppleDouble files ending in .rsrc are supported right now, this is easily expandable if needed`);

const dataFilePath = inputFilePath.slice(0, -".rsrc".length);
if(!await fileUtil.exists(dataFilePath))
	Deno.exit(xlog.error`Data file does not exist: ${dataFilePath}`);

// AppleDouble format: /mnt/compendium/documents/books/AppleSingle_AppleDouble.pdf
const br = new UInt8ArrayReader(await Deno.readFile(inputFilePath), {endianness : "be"});
assert(br.uint32(), 0x00_05_16_07);
assert(br.uint32(), 0x00_02_00_00);
br.skip(16);
const numEntries = br.uint16();
const entries = [];
for(let i=0;i<numEntries;i++)
{
	const entry = {};
	entry.entryid = br.uint32();
	entry.entryType = {
		1 : "dataFork",
		2 : "resourceFork",
		3 : "realName",
		4 : "comment",
		5 : "iconBW",
		6 : "iconColor",
		8 : "fileDates",
		9 : "finderInfo",
		10 : "macFileInfo",
		11 : "prodosFileInfo",
		12 : "msDosFileInfo",
		13 : "afpShortName",
		14 : "afpFileInfo",
		15 : "afpDirectoryId"
	}[entry.entryid];
	entry.offset = br.uint32();
	entry.length = br.uint32();

	entries.push(entry);
}

if(!entries.some(entry => entry.entryType==="resourceFork"))
	Deno.exit(xlog.error`No resourceFork entry found in AppleDouble file, unable to continue`);
if(!entries.some(entry => entry.entryType==="finderInfo"))
	Deno.exit(xlog.error`No finderInfo entry found in AppleDouble file, unable to continue`);

for(const entry of entries)
{
	br.setPOS(entry.offset);
	entry.data = br.raw(entry.length, true);
}

// MacBinary 2 format: https://files.stairways.com/other/macbinaryii-standard-info.txt
const outHeader = new Uint8Array(128);
outHeader.setUInt8(0, 0);

const macFilename = (await encodeUtil.encodeMacintosh({str : path.basename(dataFilePath), region : argv.region})).slice(0, 63);
outHeader.setUInt8(1, Math.min(63, macFilename.length));
outHeader.set(Array(63).fill(0), 2);
outHeader.set(macFilename, 2);

// finder info detailed as 'TYPE FInfo = RECORD' on page 139 of: file:///mnt/compendium/documents/books/InsideMacintosh/Inside_Macintosh_Volume_II_1985.pdf
const finderInfo = entries.find(entry => entry.entryType==="finderInfo");
outHeader.set(finderInfo.data.subarray(0, 4), 65);	// file type
outHeader.set(finderInfo.data.subarray(4, 8), 69);	// file creator
const finderInfoFlags = finderInfo.data.getUInt16BE(8);
const oldFlags = (finderInfoFlags >> 8) & 0xFF;
outHeader.setUInt8(73, oldFlags);	// original finder flags
outHeader.setUInt8(74, 0);
outHeader.setUInt16BE(75, finderInfo.data.getUInt16BE(10));	// location, x coord
outHeader.setUInt16BE(77, finderInfo.data.getUInt16BE(12));	// location, y coord
outHeader.setUInt16BE(79, finderInfo.data.getUInt16BE(14));	// folder window
outHeader.setUInt8(81, oldFlags & 0x80);	// old, locked bit
outHeader.setUInt8(82, 0);

const dataForkStat = await Deno.stat(dataFilePath);
outHeader.setUInt32BE(83, dataForkStat.size);

const resourceFork = entries.find(entry => entry.entryType==="resourceFork");
outHeader.setUInt32BE(87, resourceFork.length);

outHeader.setUInt32BE(91, (dataForkStat.mtime.getTime()/1000) + 2_082_844_800);	// creation date (number of seconds since 1904-01-01 (2082844800 is number of second between that and the unix epoch of 1970-01-01))
outHeader.setUInt32BE(95, (dataForkStat.mtime.getTime()/1000) + 2_082_844_800);	// modified date - We use the modified time for both creation and modified because that's how we do it in dexvert
outHeader.setUInt16BE(99, 0);	// length of get info comment
outHeader.setUInt8(101, finderInfoFlags & 0xFF);	// new finder flags
outHeader.set(Array(14).fill(0), 102);
outHeader.setUInt32BE(116, 0);
outHeader.setUInt16BE(120, 0);
outHeader.setUInt8(122, 129);	// version
outHeader.setUInt8(123, 129);	// min version
outHeader.setUInt16BE(124, await hashUtil.hashData("CRC-16/XMODEM", outHeader.subarray(0, 124)));	// CRC
outHeader.setUInt16BE(126, 0);	// padding?

const tmpOutFilePath = await fileUtil.genTempPath();
const tmpOutFile = await Deno.open(tmpOutFilePath, {create : true, write : true, truncate : true});
await writeAll(tmpOutFile, outHeader);

await writeAll(tmpOutFile, await Deno.readFile(dataFilePath));
let paddingLength = 128-(dataForkStat.size%128);
if(paddingLength>0)
	await writeAll(tmpOutFile, (new Uint8Array(paddingLength)).fill(0));

await writeAll(tmpOutFile, resourceFork.data);
paddingLength = 128-(resourceFork.length%128);
if(paddingLength>0)
	await writeAll(tmpOutFile, (new Uint8Array(paddingLength)).fill(0));

tmpOutFile.close();

// Make sure our resulting file isn't basically the same thing as the original file
if((await Deno.stat(tmpOutFilePath)).size===(await Deno.stat(argv.originalFilePath)).size)
{
	const beforeFilePath = await fileUtil.genTempPath();
	await runUtil.run("dd", [`if=${tmpOutFilePath}`, `of=${beforeFilePath}`, "bs=128", "skip=1"]);

	const afterFilePath = await fileUtil.genTempPath();
	await runUtil.run("dd", [`if=${argv.originalFilePath}`, `of=${afterFilePath}`, "bs=128", "skip=1"]);

	const areEqual = await fileUtil.areEqual(beforeFilePath, afterFilePath);
	await fileUtil.unlink(beforeFilePath);
	await fileUtil.unlink(afterFilePath);

	if(areEqual)
	{
		await fileUtil.unlink(tmpOutFilePath);
		Deno.exit(0);
	}
}

await fileUtil.unlink(inputFilePath);
await fileUtil.unlink(dataFilePath);
await Deno.copyFile(tmpOutFilePath, dataFilePath);
await fileUtil.unlink(tmpOutFilePath);

await Deno.utime(dataFilePath, Math.floor(dataForkStat.mtime/xu.SECOND), Math.floor(dataForkStat.mtime/xu.SECOND));
