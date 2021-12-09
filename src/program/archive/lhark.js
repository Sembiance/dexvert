import {xu} from "xu";
import {Program} from "../../Program.js";

export class lhark extends Program
{
	website   = "https://www.sac.sk/download/pack/lhark04d.zip";
	loc       = "dos";
	bin       = "LHARK.EXE";
	args      = r => ["e", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
