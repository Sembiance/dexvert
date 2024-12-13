import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class sar extends Program
{
	website   = "https://www.sac.sk/download/pack/sar1.zip";
	loc       = "dos";
	bin       = "SAR1/SAR.EXE";
	args      = r => ["e", `E:\\${path.basename(r.inFile())}`];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
