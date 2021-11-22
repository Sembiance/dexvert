import {Program} from "../../Program.js";

export class imageAlchemy extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/Image_Alchemy";
	loc = "dos";
	bin = "ALCHEMY.EXE";
	args = async r => ["-t", r.inFile(), await r.outFile("OUT.TIF")]
	chain = "convert"
}
