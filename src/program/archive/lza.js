import {Program} from "../../Program.js";

export class lza extends Program
{
	website      = "https://www.sac.sk/download/pack/lza101.zip";
	loc          = "dos";
	bin          = "LZA101/LZADOS.EXE";
	args         = r => [r.inFile({backslash : true}), "OUTFILE", "/U"];
	cwd          = r => r.outDir();
	dosData      = () => ({runIn : "out"});
	checkForDups = true;
	renameOut    = true;
}
