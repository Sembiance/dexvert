import {Program} from "../../Program.js";

export class gifblast extends Program
{
	website       = "http://fileformats.archiveteam.org/wiki/Image_Alchemy";
	loc           = "dos";
	bin           = "GIFBLAST.EXE";
	args          = r => ["-D", r.inFile({backslash : true})];
	cwd           = r => r.outDir();
	mirrorInToCWD = "copy";
	dosData       = () => ({runIn : "out"});
	renameOut     = true;
}
