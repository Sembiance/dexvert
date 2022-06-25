import {xu} from "xu";
import {Program} from "../../Program.js";

export class mdcd extends Program
{
	website   = "http://cd.textfiles.com/megarom/megarom1/ARC_LBR/MDCD10.ZIP";
	loc       = "dos";
	bin       = "MDCD.EXE";
	args      = r => ["r", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
