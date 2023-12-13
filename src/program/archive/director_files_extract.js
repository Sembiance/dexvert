import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

export class director_files_extract extends Program
{
	website       = "https://github.com/n0samu/director-files-extract";
	bin           = "python";
	args          = r => [path.join(Program.binPath("director-files-extract"), "shock.py"), r.inFile()];
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	postExec = async r =>
	{
		const outDirPath = r.outDir({absolute : true});
		const relFilePaths = await fileUtil.tree(outDirPath, {relative : true, nodir : true});
		await relFilePaths.parallelMap(async relFilePath =>
		{
			if(!relFilePath.includes("/"))
				return;

			await Deno.rename(path.join(outDirPath, relFilePath), path.join(outDirPath, path.basename(relFilePath)));
		});
	};
	renameOut     = true;
}
