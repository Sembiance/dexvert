import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class aaru extends Program
{
	website    = "https://github.com/aaru-dps/Aaru";
	package    = "app-arch/Aaru";
	bin        = "aaru";
	args       = r =>
	{
		const a = ["filesystem", "extract"];
		
		const ccdFile = (r.f?.files?.aux || []).find(auxFile => auxFile.ext.toLowerCase()===".ccd");
		a.push(ccdFile ? ccdFile.base : r.inFile());
		a.push(r.outDir());
		return a;
	};
	runOptions = ({env : {DOTNET_ROOT : "/opt/dotnet-sdk-bin-8.0"}});
	pre        = async r => await fileUtil.unlink(r.outDir({absolute : true}), {recursive : true});	// aaru requires no output dir present, it creates it
	postExec   = async r =>
	{
		// aaru outputs files in a single subdir and another within that, move em all up 1 level
		const outDirPath = r.outDir({absolute : true});
		const rootDirs = await fileUtil.tree(outDirPath, {nofile : true, depth : 1});
		if(rootDirs.length!==1)
			return;

		const subDirs = await fileUtil.tree(rootDirs[0], {nofile : true, depth : 1});
		if(subDirs.length!==1)
			return;

		// rename the root dir to a temp name just to avoid collisions
		const tmpDirName = await fileUtil.genTempPath(outDirPath);
		await Deno.rename(rootDirs[0], tmpDirName);

		const subFiles = await fileUtil.tree(path.join(tmpDirName, path.basename(subDirs[0])), {depth : 1});
		await subFiles.parallelMap(subFile => Deno.rename(subFile, path.join(outDirPath, path.basename(subFile))));
		await fileUtil.unlink(tmpDirName, {recursive : true});
	};
	renameOut = false;
}
