import {xu} from "xu";
import {XLog} from "xlog";
import {fileUtil, cmdUtil} from "xutil";

const xlog = new XLog("info");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Print out the byte offset where the EXE overlay starts",
	args :
	[
		{argid : "inputFilePath", desc : "EXE tp process", required : true}
	]
});

const size = (await Deno.stat(argv.inputFilePath)).size;
if(size<64)
	Deno.exit(0);

const dosHeader = await fileUtil.readFileBytes(argv.inputFilePath, 64);
if(dosHeader.getString(0, 2)!=="MZ")
	Deno.exit(0);

const peHeaderOffset = dosHeader.getUInt32LE(0x3C);
let overlayStartOffset;

// Try PE format first
if(peHeaderOffset>=0x40 && peHeaderOffset<size-24)
{
	const peSignature = await fileUtil.readFileBytes(argv.inputFilePath, 4, peHeaderOffset);
	if(peSignature.getString(0, 2)==="PE")
	{
		const peHeader = await fileUtil.readFileBytes(argv.inputFilePath, 24, peHeaderOffset);
		const numSections = peHeader.getUInt16LE(6);
		if(numSections>0)
		{
			const lastSecOffset = peHeaderOffset+24+peHeader.getUInt16LE(20)+((numSections-1)*40);
			if((lastSecOffset+40)<=size)
			{
				const lastSec = await fileUtil.readFileBytes(argv.inputFilePath, 24, lastSecOffset+16);
				overlayStartOffset = lastSec.getUInt32LE(4)+lastSec.getUInt32LE(0);
			}
		}
	}
}

// Fallback to MS-DOS format
if(!overlayStartOffset)
{
	const pages = dosHeader.getUInt16LE(0x04);
	const lastPageBytes = dosHeader.getUInt16LE(0x02);
	if(pages>0)
		overlayStartOffset = lastPageBytes===0 ? pages*512 : ((pages-1)*512)+lastPageBytes;
}

if(!overlayStartOffset || overlayStartOffset>=size)
	Deno.exit(0);

xlog.info`Overlay offset: ${overlayStartOffset}`;
xlog.info`hexyl -s ${overlayStartOffset} -n 128 "${argv.inputFilePath}"`;
