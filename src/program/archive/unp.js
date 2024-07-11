import {Program} from "../../Program.js";

export class unp extends Program
{
	website   = "https://sites.google.com/view/f1gpwc/file-archive/miscellaneous/exe-unpacker";
	loc       = "dos";
	bin       = "UNP.EXE";
	args      = async r => ["e", r.inFile({backslash : true}), await r.outFile("OUTFILE", {backslash : true})];
	renameOut = false;
}
