/* eslint-disable no-bitwise */
import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil} from "xutil";
import {path} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";
import {assert} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Extracts files from Mac VISE installer packages saves them to <outputDirPath>",
	opts    :
	{
		logLevel : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: warn", defaultValue : "info"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "Mac VISE Installer package to extract", required : true},
		{argid : "outputDirPath", desc : "Output dir to save icons to", required : true}
	]});

// Format from: https://pastebin.com/GwQYz2gG

const xlog = new XLog(argv.logLevel);

const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "be"});

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
