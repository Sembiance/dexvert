import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";

export class gametls extends Program
{
	website      = "https://github.com/Malvineous/libgamegraphics";
	package      = "dev-libs/libgamegraphics";
	bin          = "gametls";
	flags        = {
		type     : "The file type of the input file",
		colCount : "Number of columns in the output image. Default is 20."
	};
	args         = r => ["-X", ...(r.flags.type ? ["-t", r.flags.type] : []), r.inFile()];
	cwd          = r => r.outDir();
	postExec     = async r =>
	{
		const outDirPath = r.outDir({absolute : true});
		const fileOutputPaths = await fileUtil.tree(outDirPath, {nodir : true});
		const subImages = {};
		for(const fileOutputPath of fileOutputPaths)
		{
			const {tileid, num} = path.basename(fileOutputPath).match(/^(?<tileid>\d+)\.(?<num>\d+)\.png$/)?.groups || {};
			if(!tileid || !num)
				continue;
			
			subImages[tileid] ||= [];
			subImages[tileid].push([+num, fileOutputPath]);
		}

		await Object.entries(subImages).parallelMap(async ([tileid, filePaths]) =>
		{
			const cols = Math.min(filePaths.length, (+(r.flags.colCount || 20)));
			const rows = Math.ceil(filePaths.length/ (+(r.flags.colCount || 20)));
			await runUtil.run("montage", [...filePaths.sortMulti([([num]) => num]).map(([, filePath]) => filePath), "-tile", `${cols}x${rows}`, "-geometry", "+0+0", path.join(r.outDir({absolute : true}), `${tileid}.png`)], {timeout : xu.MINUTE*2});
			await filePaths.parallelMap(async ([, filePath]) =>
			{
				await fileUtil.unlink(filePath);
				fileOutputPaths.removeOnce(filePath);
			});
		});
	};
	renameOut    = true;
}
