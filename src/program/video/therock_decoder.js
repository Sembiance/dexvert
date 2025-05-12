import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

export class therock_decoder extends Program
{
	website        = "https://github.com/Sgeo/therock_decoder";
	package        = "games-util/therock_decoder";
	bin            = "therock_decoder";
	args           = r => [r.inFile()];
	cwd            = r => r.outDir();
	mirrorInToCWD  = "copy";
	forbidChildRun = true;
	pre            = async r =>
	{
		const outInputFile = (await fileUtil.tree(r.outDir({absolute : true})))?.[0];
		if(outInputFile)
			await Deno.rename(outInputFile, path.join(path.dirname(outInputFile), "SCIGUY.MOV"));
	};
	renameOut = false;
	notes     = "This only supports sciguy.mov but there is evidence that there exists other 3 files with a similar format. Future To-Do item I suppose.";
}
