import {xu} from "xu";
import {Program} from "../../Program.js";

export class cwunpack extends Program
{
	website   = "https://github.com/geneb/CompressionWorkshop/blob/master/CWUNPACK.EXE";
	loc       = "dos";
	bin       = "CWUNPACK.EXE";
	args      = r => [r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
