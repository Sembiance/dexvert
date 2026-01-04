import {xu} from "xu";
import {Program} from "../../Program.js";

export class xmp extends Program
{
	website = "http://xmp.sourceforge.net/";
	package = "media-sound/xmp";
	bin     = "xmp";
	args    = async r => ["--quiet", "-o", await r.outFile("out.wav"), r.inFile()];
	
	// xmp often fails to produce a valid wav but does produce a 44 byte wav file of nothing
	verify    = (r, dexFile) => dexFile.size!==44;
	renameOut = true;
	chain     = `sox[type:wav][maxDuration:${xu.MINUTE*10}]`;
}
