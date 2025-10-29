import {xu} from "xu";
import {Program} from "../../Program.js";

export class uharc extends Program
{
	loc       = "dos";
	bin       = "UHARC.EXE";
	args      = r => ["x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
