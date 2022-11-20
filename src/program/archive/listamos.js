import {Program} from "../../Program.js";
import {fileUtil} from "xutil";

export class listamos extends Program
{
	website = "https://github.com/kyz/amostools/";
	package = "dev-lang/amostools";
	bin     = "listamos";
	args    = r => [r.inFile()];
	postExec = async r =>
	{
		if(r.stdout.trim().endsWith("not an AMOS source file"))
			return;
		
		await fileUtil.writeTextFile(await r.outFile("out.amosSourceCode", {absolute : true}), r.stdout.trim());
	};
	renameOut = true;
}
