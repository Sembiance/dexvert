import {Program} from "../../Program.js";

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
		
		await Deno.writeTextFile(await r.outFile("out.amosSourceCode", {absolute : true}), r.stdout.trim());
	};
}
