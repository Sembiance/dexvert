import {Program} from "../../Program.js";

export class unpaq extends Program
{
	website   = "http://files.mpoli.fi/unpacked/software/dos/compress/quant097.zip/";
	loc       = "dos";
	bin       = "QUANTUM/UNPAQ.EXE";
	args      = r => ["-x", r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = false;
}
