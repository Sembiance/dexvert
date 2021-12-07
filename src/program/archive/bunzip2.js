import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

export class bunzip2 extends Program
{
	website  = "https://gitlab.com/federicomenaquintero/bzip2";
	package  = "app-arch/bzip2";
	bin      = "bunzip2";
	args     = r => ["--force", r.inFile()];
	postExec = async r =>
	{
		const outFilePath = path.join(r.f.root, r.f.input.name);
		if(await fileUtil.exists(outFilePath))
			await fileUtil.move(outFilePath, path.join(r.outDir({absolute : true}), "out"));
	};
}
