import {xu} from "xu";
import {Program} from "../../Program.js";

export class unpakleo extends Program
{
	website   = "https://www.sac.sk/download/pack/pakll106.zip";
	loc       = "dos";
	bin       = "PAKLEO/UNPAKLEO.EXE";
	args      = r => ["-X", "+Y", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
