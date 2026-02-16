import {xu} from "xu";
import {fileUtil} from "xutil";

export async function extractEXEOverlay(inputFilePath, outputFilePath)
{
	const size = (await Deno.stat(inputFilePath)).size;
	if(size<64)
		return;

	const dosHeader = await fileUtil.readFileBytes(inputFilePath, 64);
	if(!["MZ", "ZM"].includes(dosHeader.getString(0, 2)))
		return;

	const sigHeaderOffset = dosHeader.getUInt32LE(0x3C);
	let overlayStartOffset;

	// Try extended EXE formats via the e_lfanew pointer
	if(sigHeaderOffset>=0x40 && sigHeaderOffset+4<=size)
	{
		const sigBuf = await fileUtil.readFileBytes(inputFilePath, 4, sigHeaderOffset);
		const sig = sigBuf.getString(0, 2);

		if(sig==="PE" && sigBuf.getUInt8(2)===0 && sigBuf.getUInt8(3)===0 && sigHeaderOffset+24<=size)
			overlayStartOffset = await _getPEOverlayOffset(inputFilePath, size, sigHeaderOffset);
		else if(sig==="NE" && sigHeaderOffset+64<=size)
			overlayStartOffset = await _getNEOverlayOffset(inputFilePath, size, sigHeaderOffset);
		else if((sig==="LE" || sig==="LX") && sigHeaderOffset+0x90<=size)
			overlayStartOffset = await _getLELXOverlayOffset(inputFilePath, size, sigHeaderOffset);
	}

	// Fallback to plain DOS MZ format
	if(overlayStartOffset===undefined)
	{
		const pages = dosHeader.getUInt16LE(0x04);
		const lastPageBytes = dosHeader.getUInt16LE(0x02);
		if(pages>0)
			overlayStartOffset = lastPageBytes===0 ? pages*512 : ((pages-1)*512)+lastPageBytes;
	}

	if(overlayStartOffset===undefined || overlayStartOffset>=size)
		return;

	// Write overlay to output file using chunked I/O
	const overlaySize = size-overlayStartOffset;
	const inputFile = await Deno.open(inputFilePath, {read : true});
	try
	{
		await inputFile.seek(overlayStartOffset, Deno.SeekMode.Start);
		const outputFile = await Deno.open(outputFilePath, {write : true, create : true, truncate : true});
		try
		{
			const CHUNK_SIZE = 256*1024;
			const buf = new Uint8Array(CHUNK_SIZE);
			let remaining = overlaySize;
			while(remaining>0)
			{
				const bytesRead = await inputFile.read(buf.subarray(0, Math.min(CHUNK_SIZE, remaining)));
				if(bytesRead===null)
					break;
				await outputFile.write(buf.subarray(0, bytesRead));
				remaining -= bytesRead;
			}
		}
		finally { outputFile.close(); }
	}
	finally { inputFile.close(); }

	return overlayStartOffset;
}

// PE format — Win95, Win98, WinXP, Vista, Win7, Win10, Win11 (32-bit and 64-bit)
async function _getPEOverlayOffset(inputFilePath, size, peOffset)
{
	const peHeader = await fileUtil.readFileBytes(inputFilePath, 24, peOffset);
	const numSections = peHeader.getUInt16LE(6);
	const optHeaderSize = peHeader.getUInt16LE(20);
	const sectionTableOffset = peOffset+24+optHeaderSize;

	let maxEnd = 0;

	// Find the end of the last section's raw data on disk
	if(numSections>0 && sectionTableOffset+(numSections*40)<=size)
	{
		const sections = await fileUtil.readFileBytes(inputFilePath, numSections*40, sectionTableOffset);
		for(let i=0;i<numSections;i++)
		{
			const rawSize = sections.getUInt32LE((i*40)+16);  // SizeOfRawData
			const rawPtr  = sections.getUInt32LE((i*40)+20);  // PointerToRawData
			if(rawPtr>0 && rawSize>0)
			{
				const end = rawPtr+rawSize;
				if(end>maxEnd)
					maxEnd = end;
			}
		}
	}

	// Check IMAGE_DIRECTORY_ENTRY_SECURITY (certificate table, index 4).
	// Unlike other data directories, its VirtualAddress is a raw file offset, not an RVA.
	// Signed PE files store the certificate data AFTER all sections.
	if(optHeaderSize>=2)
	{
		const optOffset = peOffset+24;
		const readSize = Math.min(optHeaderSize, 256);
		if(optOffset+readSize<=size)
		{
			const opt = await fileUtil.readFileBytes(inputFilePath, readSize, optOffset);
			const magic = opt.getUInt16LE(0);

			let numDirsOff, dirStartOff;
			if(magic===0x10B) { numDirsOff = 92; dirStartOff = 96; }   // PE32
			else if(magic===0x20B) { numDirsOff = 108; dirStartOff = 112; }  // PE32+ (64-bit)

			if(dirStartOff!==undefined && numDirsOff+4<=readSize)
			{
				const numDirs = opt.getUInt32LE(numDirsOff);
				const certEntryOff = dirStartOff+(4*8);  // index 4, each entry 8 bytes
				if(numDirs>=5 && certEntryOff+8<=readSize)
				{
					const certAddr = opt.getUInt32LE(certEntryOff);
					const certSize = opt.getUInt32LE(certEntryOff+4);
					if(certAddr>0 && certSize>0)
					{
						const certEnd = certAddr+certSize;
						if(certEnd>maxEnd)
							maxEnd = certEnd;
					}
				}
			}
		}
	}

	// Check COFF symbol table + string table (rare in executables, seen in MinGW-linked binaries)
	const symPtr  = peHeader.getUInt32LE(12);  // PointerToSymbolTable
	const numSyms = peHeader.getUInt32LE(16);  // NumberOfSymbols
	if(symPtr>0 && numSyms>0)
	{
		const symEnd = symPtr+(numSyms*18);
		// COFF string table immediately follows; first 4 bytes = total size including those 4 bytes
		if(symEnd+4<=size)
		{
			const strSizeBuf = await fileUtil.readFileBytes(inputFilePath, 4, symEnd);
			const strTableSize = strSizeBuf.getUInt32LE(0);
			const end = symEnd+(strTableSize>=4 ? strTableSize : 4);	// eslint-disable-line unicorn/prefer-math-min-max
			if(end>maxEnd)
				maxEnd = end;
		}
		else if(symEnd>maxEnd)
		{
			maxEnd = symEnd;
		}
	}

	if(maxEnd>0)
		return maxEnd;
}

// NE format — Windows 3.0 / 3.1 (16-bit New Executable)
async function _getNEOverlayOffset(inputFilePath, size, neOffset)
{
	const ne = await fileUtil.readFileBytes(inputFilePath, 64, neOffset);
	const segCount       = ne.getUInt16LE(0x1C);
	const nonResNameSize = ne.getUInt16LE(0x20);
	const segTableRelOff = ne.getUInt16LE(0x22);
	const resTableRelOff = ne.getUInt16LE(0x24);
	const resNameRelOff  = ne.getUInt16LE(0x26);
	const nonResNameOff  = ne.getUInt32LE(0x2C);  // absolute file offset
	const alignShift     = ne.getUInt16LE(0x32);
	const segAlign       = 2**alignShift;

	let maxOffset = 0;

	// Check segment data ends
	if(segCount>0)
	{
		const segTableOff = neOffset+segTableRelOff;
		const segTableBytes = segCount*8;
		if(segTableOff+segTableBytes<=size)
		{
			const seg = await fileUtil.readFileBytes(inputFilePath, segTableBytes, segTableOff);
			for(let i=0;i<segCount;i++)
			{
				const logicalSector = seg.getUInt16LE(i*8);
				const lengthInFile  = seg.getUInt16LE((i*8)+2);
				if(logicalSector>0)
				{
					// NE spec: a length of 0 means the segment is 64KB (0x10000 bytes)
					const actualLen = lengthInFile===0 ? 0x10000 : lengthInFile;	// eslint-disable-line unicorn/numeric-separators-style
					const segEnd = (logicalSector*segAlign)+actualLen;
					if(segEnd>maxOffset)
						maxOffset = segEnd;
				}
			}
		}
	}

	// Check resource data ends (resources use their own alignment from the resource table)
	if(resTableRelOff>0 && resTableRelOff<resNameRelOff)
	{
		const resTableOff = neOffset+resTableRelOff;
		const resTableEnd = neOffset+resNameRelOff;
		const resTableBytes = resTableEnd-resTableOff;
		if(resTableBytes>=2 && resTableEnd<=size)
		{
			const res = await fileUtil.readFileBytes(inputFilePath, resTableBytes, resTableOff);
			const rscAlignShift = res.getUInt16LE(0);
			if(rscAlignShift<=31)
			{
				const rscAlign = 2**rscAlignShift;
				let pos = 2;

				while(pos+8<=res.length)
				{
					const typeID = res.getUInt16LE(pos);
					if(typeID===0)
						break;
					const count = res.getUInt16LE(pos+2);
					pos += 8;  // TYPEINFO: typeID(2) + count(2) + reserved(4)

					for(let j=0;j<count && pos+12<=res.length;j++)
					{
						const rnOff = res.getUInt16LE(pos);
						const rnLen = res.getUInt16LE(pos+2);
						pos += 12;  // NAMEINFO: offset(2)+length(2)+flags(2)+id(2)+handle(2)+usage(2)

						if(rnOff>0 && rnLen>0)
						{
							// Both offset and length are in resource alignment units
							const resEnd = (rnOff+rnLen)*rscAlign;
							if(resEnd>maxOffset)
								maxOffset = resEnd;
						}
					}
				}
			}
		}
	}

	// Non-resident name table (absolute file offset, typically the last NE structure)
	if(nonResNameOff>0 && nonResNameSize>0)
	{
		const nonResEnd = nonResNameOff+nonResNameSize;
		if(nonResEnd>maxOffset)
			maxOffset = nonResEnd;
	}

	if(maxOffset>0)
		return maxOffset;
}

// LE/LX format — VxD drivers, DOS extenders (DOS/4GW), OS/2 2.x+ executables
async function _getLELXOverlayOffset(inputFilePath, size, leOffset)
{
	const hdr = await fileUtil.readFileBytes(inputFilePath, 0x90, leOffset);
	const sig          = hdr.getString(0, 2);
	const numPages     = hdr.getUInt32LE(0x14);
	const pageSize     = hdr.getUInt32LE(0x28);
	const field2C      = hdr.getUInt32LE(0x2C);   // LE: bytes on last page; LX: page offset shift
	const dataPagesOff = hdr.getUInt32LE(0x80);    // absolute file offset
	const nonResOff    = hdr.getUInt32LE(0x88);    // absolute file offset
	const nonResLen    = hdr.getUInt32LE(0x8C);

	let maxOffset = 0;

	if(dataPagesOff>0 && numPages>0 && pageSize>0)
	{
		if(sig==="LX")
		{
			// LX: pages can be non-contiguous/compressed; scan the object page table
			const pageOffShift = field2C;
			const pageMapOff = leOffset+hdr.getUInt32LE(0x48);  // relative to LE/LX header
			if(pageMapOff+(numPages*8)<=size)
			{
				const pm = await fileUtil.readFileBytes(inputFilePath, numPages*8, pageMapOff);
				for(let i=0;i<numPages;i++)
				{
					const pgOff   = pm.getUInt32LE(i*8);       // page data offset (in shift units)
					const pgSize  = pm.getUInt16LE((i*8)+4);   // actual data size on disk
					const pgFlags = pm.getUInt16LE((i*8)+6);

					// Skip invalid (2) and zero-filled (3) pages — no file data
					if(pgFlags===2 || pgFlags===3)
						continue;
					if(pgSize>0)
					{
						const end = dataPagesOff+(pgOff*(2**pageOffShift))+pgSize;
						if(end>maxOffset)
							maxOffset = end;
					}
				}
			}
			else
			{
				// Can't read page table; use conservative estimate
				const end = dataPagesOff+(numPages*pageSize);
				if(end>maxOffset)
					maxOffset = end;
			}
		}
		else
		{
			// LE: pages are stored contiguously; last page may be shorter
			const lastSize = (field2C>0 && field2C<=pageSize) ? field2C : pageSize;
			const end = dataPagesOff+((numPages-1)*pageSize)+lastSize;
			if(end>maxOffset)
				maxOffset = end;
		}
	}

	// Non-resident name table (absolute file offset)
	if(nonResOff>0 && nonResLen>0)
	{
		const nonResEnd = nonResOff+nonResLen;
		if(nonResEnd>maxOffset)
			maxOffset = nonResEnd;
	}

	if(maxOffset>0)
		return maxOffset;
}
