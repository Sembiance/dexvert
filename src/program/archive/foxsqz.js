import {xu} from "xu";
import {Program} from "../../Program.js";

export class foxsqz extends Program
{
	website   = "https://www.sac.sk/download/pack/ain232.exe";
	loc       = "dos";
	bin       = "FOXSQZ/FOXSQZ.EXE";
	args      = r => ["U", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
