import {xu} from "xu";
import {Program, CONVERT_PNG_ARGS} from "./Program.js";
import {fileUtil, runUtil, sysUtil} from "xutil";
import {path} from "std";
import {DexFile} from "./DexFile.js";

// Based on file extension or an r.flag.convertAsExt hint, will just try to convert the file to a PNG
// This introduces a slight risk of generating a garbage PNG file, but the speed gains are worth it
// Currently only called by other programs that generate lots of sub files like deark and resource_dasm
export async function quickConvertImages(r, fileOutputPaths)
{
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
			await runUtil.run("convert", [fileOutputPath, ...CONVERT_PNG_ARGS, convertedFilePath], runOpts);
		}
		else if([".tif", ".tiff"].includesAny(extMatches))
		{
			await runUtil.run("convert", [fileOutputPath, "-alpha", "off", ...CONVERT_PNG_ARGS, convertedFilePath], runOpts);	// some .tiff files like hi158.tiff convert as 100% transparent but this fixes it
		}
		else if([".qtif"].includesAny(extMatches))
		{
			await runUtil.run("nconvert", ["-out", "png", "-o", convertedFilePath, fileOutputPath], runOpts);
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
				await fileUtil.move(combinedFiles[0].absolute, convertedFilePath);
				if(combinedFiles.length>1)
					r.xlog.warn`Recombining pict produced more than 1 output file, only keeping the first one!`;
			}

			await combinedR.unlinkHomeOut();
		}
		else if(r.flags.alwaysConvert)
		{
			await runUtil.run("convert", [fileOutputPath, "-alpha", "off", ...CONVERT_PNG_ARGS, convertedFilePath], runOpts);
		}
		else
		{
			return;
		}

		if(await fileUtil.exists(convertedFilePath))
		{
			const fileInfo = await Deno.lstat(fileOutputPath).catch(() => {});
			if(fileInfo)
				await Deno.utime(convertedFilePath, Math.floor(fileInfo.mtime.getTime()/xu.SECOND), Math.floor(fileInfo.mtime.getTime()/xu.SECOND));
			
			await fileUtil.unlink(fileOutputPath);
			filePathsToRemove.push(fileOutputPath);
		}
	}, await optimalParallelism(fileOutputPaths.length));

	for(const filePathToRemove of filePathsToRemove)
		fileOutputPaths.removeOnce(filePathToRemove);
}

export async function optimalParallelism(numFiles)
{
	if(numFiles<5)
		return 1;

	let optimalCount = 1;
	const idleUsage = await sysUtil.getCPUIdleUsage();
	optimalCount = Math.max(1, Math.floor(idleUsage.scale(0, 100, 1, navigator.hardwareConcurrency*0.50)));
	return optimalCount;
}
