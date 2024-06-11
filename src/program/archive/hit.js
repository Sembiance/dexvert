import {xu} from "xu";
import {Program} from "../../Program.js";

export class hit extends Program
{
	website   = "https://www.sac.sk/download/pack/hit.arj";
	loc       = "dos";
	bin       = "HIT.EXE";
	args      = r => ["x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
