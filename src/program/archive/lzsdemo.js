import {Program} from "../../Program.js";

export class lzsdemo extends Program
{
	website   = "https://www.sac.sk/download/pack/lzs221.zip";
	loc       = "dos";
	bin       = "LZSDEMO.EXE";
	unsafe    = true;
	args      = async r => [r.inFile({backslash : true}), await r.outFile("OUTFILE", {backslash : true})];
	renameOut = true;
}
