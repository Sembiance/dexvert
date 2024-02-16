import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

export class pc98ripper extends Program
{
	website   = "https://gitlab.com/bunnylin/98ripper";
	package   = "app-arch/98ripper";
	bin       = "98ripper";
	args      = r => [`--output=${r.outDir()}`, r.inFile()];
	postExec  = async r =>
	{
		// 98ripper always outputs files in a single subdir, move em all up 1 level
		const outDirPath = r.outDir({absolute : true});
		const outDirs = await fileUtil.tree(outDirPath, {nofile : true, depth : 1});
		if(outDirs.length!==1)
			return;
		const tmpDirName = await fileUtil.genTempPath(outDirPath);
		await Deno.rename(outDirs[0], tmpDirName);

		const subFiles = await fileUtil.tree(tmpDirName, {depth : 1});
		await subFiles.parallelMap(subFile => Deno.rename(subFile, path.join(outDirPath, path.basename(subFile))));
	};
	renameOut = false;
}
