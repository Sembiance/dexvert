import {xu} from "xu";
import {Program} from "../../Program.js";

export class semone extends Program
{
	website   = "https://www.sac.sk/download/pack/semone06.zip";
	loc       = "dos";
	bin       = "SEMONE.EXE";
	args      = r => ["x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
