import {Program} from "../../Program.js";

export class cup386 extends Program
{
	loc       = "dos";
	bin       = "CUP386/CUP386.COM";
	args      = async r => [r.inFile({backslash : true}), await r.outFile("OUTFILE", {backslash : true}), "/1"];
	renameOut = true;
}
