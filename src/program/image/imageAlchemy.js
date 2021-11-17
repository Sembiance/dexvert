import {Program} from "../../Program.js";
import {path} from "std";

export class imageAlchemy extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/Image_Alchemy";
	loc = "dos";
	bin = "ALCHEMY.EXE";
	args = r => ["-t", r.inFile(), r.outFile("OUT.TIF")]
	chain = "convert"
}
