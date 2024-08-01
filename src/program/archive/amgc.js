import {xu} from "xu";
import {Program} from "../../Program.js";

export class amgc extends Program
{
	website   = "https://www.sac.sk/download/pack/amgc22.zip";
	loc       = "dos";
	bin       = "AMGC.EXE";
	args      = r => ["x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
