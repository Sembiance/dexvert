import {Program} from "../../Program.js";

export class mwaw2text extends Program
{
	website    = "https://sourceforge.net/p/libmwaw/wiki/Home/";
	package    = "app-text/libmwaw";
	bin        = "mwaw2text";
	unsafe     = true;
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.txt")});
	verify     = (r, dexFile) => dexFile.size>2 && dexFile.size!==32;	// 32 byte long file is just text: ERROR: Unsupported file format!
	renameOut  = true;
}
