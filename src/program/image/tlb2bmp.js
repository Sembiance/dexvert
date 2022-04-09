import {Program} from "../../Program.js";

export class tlb2bmp extends Program
{
	website   = "http://frua.rosedragon.org/pc/misc/tlb2bmp.txt";
	loc       = "dos";
	bin       = "TLB2BMP.EXE";
	unsafe    = true;
	args      = r => [r.inFile({backslash : true})];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = true;
	chain     = "dexvert[asFormat:image/bmp] -> autoCropImage[borderColor:#000000]";
}
