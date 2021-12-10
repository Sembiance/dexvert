import {Program} from "../../Program.js";

export class dgiwind extends Program
{
	website   = "http://cd.textfiles.com/carousel344/003/CONV125.ZIP";
	unsafe    = true;
	loc       = "dos";
	bin       = "CONV125/DGIWIND.EXE";
	args      = r => [r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = true;
	chain     = "dexvert[asFormat:image/msp]";
}
