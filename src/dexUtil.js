import {xu} from "xu";
import {Program, CONVERT_PNG_ARGS} from "./Program.js";
import {fileUtil, runUtil, sysUtil} from "xutil";
import {path} from "std";
import {DexFile} from "./DexFile.js";

export const DEXRPC_HOST = "127.0.0.1";
export const DEXRPC_PORT = 17750;
export const DEV_MACHINE = ["crystalsummit", "ridgeport"].includes(Deno.hostname());

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
