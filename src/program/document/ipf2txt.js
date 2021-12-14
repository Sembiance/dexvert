import {Program} from "../../Program.js";

export class ipf2txt extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	loc       = "dos";
	bin       = "IPF2TXT.EXE";
	args      = async r => [r.inFile({backslash : true}), "80", ">", await r.outFile("out.txt", {backslash : true})];
	renameOut = true;
	chain     = "iconv[fromEncoding:CP866]";
}
