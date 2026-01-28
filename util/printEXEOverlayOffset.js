import {xu} from "xu";
import {XLog} from "xlog";
import {fileUtil, cmdUtil} from "xutil";

const xlog = new XLog("info");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Print out the byte offset where the EXE overlay starts",
	args :
	[
		{argid : "inputFilePath", desc : "EXE to process", required : true}
	]
});

const inputFilePath = argv.inputFilePath;
const size = (await Deno.stat(inputFilePath)).size;
if(size<64)
	Deno.exit(0);

const dosHeader = await fileUtil.readFileBytes(inputFilePath, 64);
if(!["MZ", "ZM"].includes(dosHeader.getString(0, 2)))
	Deno.exit(0);

const sigHeaderOffset = dosHeader.getUInt32LE(0x3C);
let overlayStartOffset;

// Try PE format first
if(sigHeaderOffset>=0x40 && sigHeaderOffset<=(size-24))
{
	const sigHeader = await fileUtil.readFileBytes(inputFilePath, 24, sigHeaderOffset);
	const signature = sigHeader.getString(0, 2);
	if(signature==="PE")
	{
		const numSections = sigHeader.getUInt16LE(6);
		const sectionTableOffset = sigHeaderOffset+24+sigHeader.getUInt16LE(20);
		if(numSections>0 && (sectionTableOffset+(numSections*40))<=size)
		{
			let maxEnd = 0;

			const sections = await fileUtil.readFileBytes(inputFilePath, numSections*40, sectionTableOffset);
			for(let i=0;i<numSections;i++)
			{
				const end = sections.getUInt32LE((i*40)+16)+sections.getUInt32LE((i*40)+20);
				if(end>maxEnd)
					maxEnd = end;
			}

			if(maxEnd>0)
				overlayStartOffset = maxEnd;
		}
	}
	else if(signature==="NE" && sigHeaderOffset<=(size-56))
	{
		const neHeader = await fileUtil.readFileBytes(inputFilePath, 56, sigHeaderOffset);
		const segmentTableOffset = sigHeaderOffset+neHeader.getUInt16LE(0x22);
		const segmentCount = neHeader.getUInt16LE(0x1C);
		const alignmentShift = neHeader.getUInt16LE(0x32);
		const nonResNameTableOffset = neHeader.getUInt32LE(0x2C);
		const nonResNameTableSize = neHeader.getUInt16LE(0x20);

		let maxOffset = 0;

		if(segmentCount>0 && segmentTableOffset<size)
		{
			const segTableSize = segmentCount*8;
			if((segmentTableOffset+segTableSize)<=size)
			{
				const segTable = await fileUtil.readFileBytes(inputFilePath, segTableSize, segmentTableOffset);
				const align = 2**alignmentShift;

				for(let i=0; i<segmentCount; i++)
				{
					const logicalSector = segTable.getUInt16LE(i*8);
					const lengthInFile = segTable.getUInt16LE((i*8)+2);

					if(logicalSector>0 && lengthInFile>0)
					{
						const segEnd = (logicalSector*align)+lengthInFile;
						if(segEnd>maxOffset)
							maxOffset = segEnd;
					}
				}
			}
		}

		if(nonResNameTableOffset>0 && nonResNameTableSize>0)
		{
			const nonResEnd = nonResNameTableOffset+nonResNameTableSize;
			if(nonResEnd>maxOffset)
				maxOffset = nonResEnd;
		}

		if(maxOffset>0)
			overlayStartOffset = maxOffset;
	}
}

// Fallback to MS-DOS format
if(overlayStartOffset===undefined)
{
	const pages = dosHeader.getUInt16LE(0x04);
	const lastPageBytes = dosHeader.getUInt16LE(0x02);
	if(pages>0)
		overlayStartOffset = lastPageBytes===0 ? pages*512 : ((pages-1)*512)+lastPageBytes;
}

if(overlayStartOffset===undefined || overlayStartOffset>=size)
	Deno.exit(0);

xlog.info`Overlay offset: ${overlayStartOffset}`;
xlog.info`hexyl -s ${overlayStartOffset} -n 128 "${inputFilePath}"`;
