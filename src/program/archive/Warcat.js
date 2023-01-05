import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class Warcat extends Program
{
	website  = "https://pypi.org/project/Warcat";
	package  = "app-arch/Warcat";
	bin      = "python3";
	args     = r => ["-m", "warcat", "--output-dir", r.outDir(), "--keep-going", "extract", r.inFile()];
	postExec = async r =>
	{
		const fileOutputPaths = await fileUtil.tree(r.outDir({absolute : true}), {nodir : true});
		await fileOutputPaths.parallelMap(async fileOutputPath =>
		{
			const dirname = path.dirname(fileOutputPath);
			const filename = path.basename(fileOutputPath);
			for(const suffix of ["", ...([].pushSequence(1, 10).map(v => v.toString()))])
			{
				const newFilePath = path.join(dirname, filename==="_" ? `index${suffix}.html` : `${filename.substring(0, filename.length-1)}${suffix}`);
				if(fileOutputPaths.includes(newFilePath))
					continue;
				
				await Deno.rename(fileOutputPath, newFilePath);
				break;
			}
		});
	};
	renameOut = false;
}
