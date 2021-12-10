import {xu} from "xu";
import {Program} from "../../Program.js";

export class ain extends Program
{
	website   = "https://www.sac.sk/download/pack/ain232.exe";
	loc       = "dos";
	bin       = "AIN.EXE";
	args      = r => ["x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out", keys : [{delay : xu.SECOND*4}, ["Enter"]]});
	renameOut = false;
}
