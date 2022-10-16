import {Program} from "../../Program.js";

export class hap306 extends Program
{
	website       = "https://archive.org/details/msdos_festival_HAPPAH21";
	loc           = "dos";
	bin           = "PAH3.EXE";
	args          = r => ["e", r.inFile({backslash : true}), "*.*"];
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	dosData       = () => ({runIn : "out"});
	renameOut     = false;
}
