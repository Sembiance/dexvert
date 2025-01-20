import {xu} from "xu";
import {Program} from "../../Program.js";

export class bsa extends Program
{
	website   = "https://www.sac.sk/download/pack/bsa.zip";
	loc       = "dos";
	bin       = "BSA/BSA.EXE";
	args      = r => ["x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
