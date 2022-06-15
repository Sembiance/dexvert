import {Program} from "../../Program.js";

export class hap210 extends Program
{
	website       = "https://archive.org/details/msdos_festival_HAPPAH21";
	loc           = "dos";
	bin           = "PAH21PD.EXE";
	args          = r => [r.inFile({backslash : true})];
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	dosData       = () => ({runIn : "out"});
	renameOut     = true;
}
