import {xu} from "xu";
import {Program} from "../../Program.js";

export class yac extends Program
{
	website   = "https://www.sac.sk/download/pack/yac102.zip";
	loc       = "dos";
	bin       = "YAC102/YAC.EXE";
	args      = r => ["x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
