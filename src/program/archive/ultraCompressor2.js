import {Program} from "../../Program.js";

export class ultraCompressor2 extends Program
{
	website   = "http://files.mpoli.fi/unpacked/software/dos/compress/quant097.zip/";
	loc       = "dos";
	bin       = "ULTRACMP/UC.EXE";
	args      = r => ["ES", r.inFile({backslash : true}).toUpperCase()];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
