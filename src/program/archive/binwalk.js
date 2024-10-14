import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

export class binwalk extends Program
{
	website = "https://github.com/OSPG/binwalk";
	package = "app-misc/binwalk";
	flags   = {
		"all" : "Set this flag to extract all files found within the file"
	};
	bin          = "binwalk";
	args         = r => [...(r.flags.all ? ["-D", ".*"] : ["-e"]), `--directory=${r.outDir()}`, r.inFile()];
	checkForDups = true;
	
	postExec = async r =>
	{
		// if we just have a single output dir at the bas level, move it on up
		const outDirPath = r.outDir({absolute : true});
		const outDirs = await fileUtil.tree(outDirPath, {depth : 1});
		if(outDirs.length!==1)
			return;

		if(!(await Deno.lstat(outDirs[0])).isDirectory)
			return;

		// rename the root dir to a temp name just to avoid collisions
		const tmpDirName = await fileUtil.genTempPath(outDirPath);
		await Deno.rename(outDirs[0], tmpDirName);

		const subFiles = await fileUtil.tree(tmpDirName, {depth : 1});
		await subFiles.parallelMap(subFile => Deno.rename(subFile, path.join(outDirPath, path.basename(subFile))));
	};
	renameOut = false;
}
