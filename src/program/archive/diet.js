import {Program} from "../../Program.js";

export class diet extends Program
{
	website   = "http://fileformats.archiveteam.org/wiki/DIET_(compression)";
	loc       = "dos";
	bin       = "DIET.EXE";
	args      = r => ["-RA", `-O${r.outDir({backslash : true})}\\OUTFILE`, r.inFile({backslash : true})];
	renameOut = true;
}
