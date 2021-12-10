import {Program} from "../../Program.js";

export class openmpt123 extends Program
{
	website = "https://lib.openmpt.org/libopenmpt/";
	package = "media-sound/openmpt123";
	bin     = "openmpt123";
	args    = async r => ["--batch", "--output", await r.outFile("out.wav"), r.inFile()];
	
	// openmpt123 often fails to produce a valid wav but does produce a 88 byte wav file of nothing
	verify    = (r, dexFile) => dexFile.size!==88;
	renameOut = true;
	chain     = "sox";
}
