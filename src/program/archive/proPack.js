import {xu} from "xu";
import {Program} from "../../Program.js";

export class proPack extends Program
{
	website   = "http://old-dos.ru/index.php?page=files&mode=files&do=show&id=5325";
	loc       = "dos";
	flags   = {
		flat : "Extract flat, this can fix issues with some archives like GRAPHICS.RNC"
	};
	bin       = "PP219.EXE";
	args      = r => [r.flags.flat ? "e" : "x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
