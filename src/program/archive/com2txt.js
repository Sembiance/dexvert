import {xu} from "xu";
import {Program} from "../../Program.js";

export class com2txt extends Program
{
	website   = "http://fileformats.archiveteam.org/wiki/Com2txt";
	loc       = "dos";
	bin       = "COM2TXT.EXE";
	args      = async r => ["-r", r.inFile({backslash : true}), await r.outFile("out.com")];
	renameOut = true;
}
