import {xu} from "xu";
import {Program} from "../../Program.js";

export class ybs extends Program
{
	website   = "https://www.sac.sk/download/pack/ybs003fd.zip";
	loc       = "dos";
	bin       = "YBS/YBS.EXE";
	args      = r => ["-d", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
