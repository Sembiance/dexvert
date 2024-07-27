import {xu} from "xu";
import {Program} from "../../Program.js";

export class akt extends Program
{
	website   = "https://www.sac.sk/download/pack/akt070b5.zip";
	loc       = "dos";
	bin       = "AKT.EXE";
	args      = r => ["x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
