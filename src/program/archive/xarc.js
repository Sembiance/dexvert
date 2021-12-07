import {Program} from "../../Program.js";

export class xarc extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/ARC_(compression_format)#ARC_Plus";
	loc     = "dos";
	bin     = "XARC.EXE";
	args    = r => [r.inFile({backslash : true}), r.outDir({backslash : true})];
}
