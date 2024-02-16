import {Program} from "../../Program.js";

export class telepaintConvert extends Program
{
	website   = "https://vetusware.com/download/TelePaint%203.0/?id=6656";
	loc       = "dos";
	bin       = "TPCONVRT.EXE";
	args      = r => [r.inFile({backslash : true}), "OUT.PCX", "/f"];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = true;
	chain     = "dexvert[asFormat:image/pcx]";
}
