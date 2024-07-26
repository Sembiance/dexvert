import {xu} from "xu";
import {Program} from "../../Program.js";

export class uharcd extends Program
{
	website   = "https://www.sac.sk/download/pack/uharc06b.zip";
	loc       = "dos";
	bin       = "UHARCD.EXE";
	args      = r => ["x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
