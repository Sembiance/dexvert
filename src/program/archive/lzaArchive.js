import {Program} from "../../Program.js";

export class lzaArchive extends Program
{
	website   = "https://www.sac.sk/download/pack/lza101.zip";
	loc       = "dos";
	bin       = "LZA101/LZADOS.EXE";
	args      = r => [r.inFile({backslash : true}), `E:\\${r.f.outDir.base}`, "/X"];
	renameOut = false;
}
