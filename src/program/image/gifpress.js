import {xu} from "xu";
import {Program} from "../../Program.js";

export class gifpress extends Program
{
	website       = "https://www.sac.sk/download/pack/bsa.zip";
	loc           = "dos";
	bin           = "GIFPRESS/GIFPRESS.EXE";
	args          = r => [r.inFile({backslash : true})];
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	dosData       = () => ({runIn : "out"});
	renameOut     = false;
}
