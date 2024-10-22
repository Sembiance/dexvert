import {xu} from "xu";
import {Program} from "../../Program.js";

export class uncrush extends Program
{
	website   = "http://cd.textfiles.com/pdos9606/ARCHIVER/TOOLS/CRUSH18.ZIP";
	loc       = "dos";
	bin       = "CRUSH18/UNCRUSH.EXE";
	args      = r => [r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
