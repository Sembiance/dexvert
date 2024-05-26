/* eslint-disable no-bitwise */
import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil} from "xutil";
import {path} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";
import {assert} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Extracts data from PH Video files",
	opts    :
	{
		logLevel : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: warn", defaultValue : "info"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "PH Video file to extract", required : true},
		{argid : "outputDirPath", desc : "Output dir to save icons to", required : true}
	]});

// Format from: https://wiki.multimedia.cx/index.php/Total_Multimedia_PH

const xlog = new XLog(argv.logLevel);

const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});

assert(reader.str(2)==="PH");

const prevChunkSize = reader.uint32();
const currentChunkSize = reader.uint32();
const followingChunkSize = reader.uint16();
reader.skip(2);
const subChunks = reader.uint16();

xlog.info`${{prevChunkSize, currentChunkSize, followingChunkSize, subChunks}}`;

for(let i=0;i<subChunks;i++)
{
	const chunkid = reader.uint16();
	const chunkSize = reader.uint16();
	xlog.info`${{i, chunkid : chunkid.toString(16), chunkSize}}`;
	reader.skip(chunkSize);
}

xlog.info`done ${reader.pos} remaining: ${reader.remaining}`;

/*
// SVCT
assert(reader.str(4)==="SVCT");
reader.skip(32);
const cvctOffset = reader.uint32();
if(cvctOffset===0)
	Deno.exit(xlog.error`No CVCT offset found`);

assert(cvctOffset<reader.length());

// CVCT
reader.setPOS(cvctOffset);
assert(reader.str(4)==="CVCT");
const chunkSize = reader.uint32();
reader.skip(6);
const numEntries = reader.uint32();
reader.skip(2);
xlog.info`numEntries: ${numEntries}   chunkSize: ${chunkSize}  pos: ${reader.pos}`;

for(let i=0;i<numEntries;i++)
{
	const entryType = reader.str(4);
	if(entryType==="DVCT")
	{
		reader.skip(76);
		const nameLength = reader.uint8();
		reader.skip(7);	// sometimes it's skip (1). not sure how to tell which one to use
		const name = reader.str(nameLength);
		xlog.info`${{nameLength, name}}`;
	}
	else if(entryType==="FVCT")
	{
		reader.skip(40);
		const type = reader.str(4);
		const creator = reader.str(4);
		reader.skip(16);
		const compressedDataForkSize = reader.uint32();
		const uncompressedDataForkSize = reader.uint32();
		const compressedResourceForkSize = reader.uint32();
		const uncompressedResourceForkSize = reader.uint32();
		reader.skip(38);
		const nameLength = reader.uint8();
		reader.skip(1);
		const name = reader.str(nameLength);
		xlog.info`${{type, creator, compressedDataForkSize, uncompressedDataForkSize, compressedResourceForkSize, uncompressedResourceForkSize, nameLength, name}}`;
	}
	else if(entryType==="PACK")
	{
		// sometimes this is at the end after numEntries, sometimes it's the first entry haven't
	}
	else
	{
		Deno.exit(xlog.error`Unknown entry type: ${entryType}`);
	}
}

xlog.info`done ${reader.pos}`;
*/
