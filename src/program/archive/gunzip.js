import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

export class gunzip extends Program
{
	website  = "https://www.gnu.org/software/gzip/";
	package  = "app-arch/gzip";
	bin      = "gunzip";
	args     = r => ["--force", r.inFile()];
	postExec = async r =>
	{
		const outFilePath = path.join(r.f.root, r.f.input.name);
		if(await fileUtil.exists(outFilePath))
			await fileUtil.move(outFilePath, path.join(r.outDir({absolute : true}), "out"));
	};
}
