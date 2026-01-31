import {xu} from "xu";
import {Program, CONVERT_PNG_ARGS} from "./Program.js";
import {fileUtil, runUtil, sysUtil} from "xutil";
import {path} from "std";
import {DexFile} from "./DexFile.js";
import {init as initPrograms} from "./program/programs.js";
import {init as initFormats} from "./format/formats.js";

export const DEXRPC_HOST = "127.0.0.1";
export const DEXRPC_PORT = 17750;
export const DEV_MACHINE = ["crystalsummit", "eaglehollow"].includes(Deno.hostname());

// Based on file extension or an r.flag.convertAsExt hint, will just try to convert the file to a PNG
// This introduces a slight risk of generating a garbage PNG file, but the MASSIVE speed gains are worth it
// Currently only called by other programs that generate lots of sub files like deark and resource_dasm
export async function quickConvertImages(r, fileOutputPaths)
{
	r.quickConvertMap ||= {};
	const runOpts = {timeout : xu.MINUTE};
	const outDirPath = r.outDir({absolute : true});
	const filePathsToRemove = [];
	await fileOutputPaths.parallelMap(async fileOutputPath =>
	{
		const ext = path.extname(fileOutputPath);
		if(r.flags.deleteADF && ext.toLowerCase()===".adf")
		{
			filePathsToRemove.push(fileOutputPath);
			return await fileUtil.unlink(fileOutputPath);
		}

		let convertedFilePath = path.join(outDirPath, `${path.basename(fileOutputPath, ext)}.png`);
		const extMatches = [ext.toLowerCase(), ...(r.flags.convertAsExt ? [r.flags.convertAsExt] : [])];
		if([".bmp", ".jp2"].includesAny(extMatches))
		{
			await runUtil.run("magick", [fileOutputPath, ...CONVERT_PNG_ARGS, convertedFilePath], runOpts);
		}
		else if([".tif", ".tiff"].includesAny(extMatches))
		{
			await runUtil.run("magick", [fileOutputPath, "-alpha", "off", ...CONVERT_PNG_ARGS, convertedFilePath], runOpts);	// some .tiff files like hi158.tiff convert as 100% transparent but this fixes it
		}
		else if([".qtif"].includesAny(extMatches))
		{
			const subR = await Program.runProgram("deark[mac]", await DexFile.create(fileOutputPath), {xlog : r.xlog});
			const subFiles = Array.force(subR?.f?.files?.new || []);
			if(subFiles.length)
			{
				convertedFilePath = path.join(outDirPath, `${path.basename(fileOutputPath, ext)}${subFiles[0].ext}`);
				await fileUtil.move(subFiles[0].absolute, convertedFilePath);
			}

			await subR.unlinkHomeOut();
		}
		else if([".eps"].includesAny(extMatches))
		{
			const combinedR = await Program.runProgram("ps2pdf[svg]", await DexFile.create(fileOutputPath), {xlog : r.xlog});
			const combinedFiles = Array.force(combinedR?.f?.files?.new || []);
			if(combinedFiles.length)
			{
				convertedFilePath = path.join(outDirPath, `${path.basename(fileOutputPath, ext)}.svg`);
				await fileUtil.move(combinedFiles[0].absolute, convertedFilePath);
				if(combinedFiles.length>1)
					r.xlog.warn`Chaining to EPS produced more than 1 output file, only keeping the first one!`;
			}
			await combinedR.unlinkHomeOut();
		}
		else if([".pict"].includesAny(extMatches))
		{
			const combinedR = await Program.runProgram("deark[mac][recombine]", await DexFile.create(fileOutputPath), {xlog : r.xlog});
			const combinedFiles = Array.force(combinedR?.f?.files?.new || []);
			if(combinedFiles.length)
			{
				convertedFilePath = path.join(outDirPath, `${path.basename(fileOutputPath, ext)}${combinedFiles[0].ext}`);
				await fileUtil.move(combinedFiles[0].absolute, convertedFilePath);
				if(combinedFiles.length>1)
					r.xlog.warn`Recombining pict produced more than 1 output file, only keeping the first one!`;
			}

			await combinedR.unlinkHomeOut();
		}
		else if([".pcd"].includesAny(extMatches))
		{
			convertedFilePath = path.join(outDirPath, `${path.basename(fileOutputPath, ext)}.jpg`);
			await runUtil.run("pcdtojpeg", ["-q", "100", fileOutputPath, convertedFilePath], runOpts);
		}
		else if(r.flags.alwaysConvert)
		{
			await runUtil.run("magick", [fileOutputPath, "-alpha", "off", ...CONVERT_PNG_ARGS, convertedFilePath], runOpts);
		}
		else
		{
			return;
		}

		if(await fileUtil.exists(convertedFilePath))
		{
			r.quickConvertMap[path.relative(outDirPath, fileOutputPath)] = path.relative(outDirPath, convertedFilePath);

			const fileInfo = await Deno.lstat(fileOutputPath).catch(() => {});
			if(fileInfo)
				await Deno.utime(convertedFilePath, Math.floor(fileInfo.mtime.getTime()/xu.SECOND), Math.floor(fileInfo.mtime.getTime()/xu.SECOND));
			
			await fileUtil.unlink(fileOutputPath);
			filePathsToRemove.push(fileOutputPath);
		}
	}, await sysUtil.optimalParallelism(fileOutputPaths.length));

	for(const filePathToRemove of filePathsToRemove)
		fileOutputPaths.removeOnce(filePathToRemove);
}

export async function getEXEOverlayOffset(inputFilePath, size)
{
	size ||= (await Deno.stat(inputFilePath)).size;
	if(size<64)
		return;

	const dosHeader = await fileUtil.readFileBytes(inputFilePath, 64);
	if(!["MZ", "ZM"].includes(dosHeader.getString(0, 2)))
		return;

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
		return;

	return overlayStartOffset;
}


export async function initRegistry(xlog)
{
	await initPrograms(xlog);
	await initFormats(xlog);
}
