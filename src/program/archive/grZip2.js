import {Program} from "../../Program.js";

export class grZip2 extends Program
{
	website   = "https://www.sac.sk/files.php?d=7&l=";
	loc       = "dos";
	bin       = "GRZIPII.EXE";
	args      = async r => ["d", r.inFile({backslash : true}), await r.outFile("OUTFILE", {backslash : true})];
	renameOut = true;
}
