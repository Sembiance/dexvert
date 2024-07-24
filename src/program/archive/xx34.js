import {xu} from "xu";
import {Program} from "../../Program.js";

export class xx34 extends Program
{
	website   = "https://www.sac.sk/download/utilfile/xx3402.zip";
	loc       = "dos";
	bin       = "XX3402.EXE";
	args      = r => ["D", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
