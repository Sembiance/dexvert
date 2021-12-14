import {xu} from "xu";
import {Program} from "../../Program.js";

export class antiword extends Program
{
	website    = "http://www.winfield.demon.nl";
	package    = "app-text/antiword";
	unsafe     = true;
	bin        = "antiword";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.txt")});
	renameOut  = true;
	verify       = (r, dexFile) =>
	{
		if(dexFile.size>xu.MB*20)
			return true;

		if(r.stderr.toLowerCase().includes("encrypted documents are not supported"))
		{
			r.meta.passwordProtected = true;
			return false;
		}

		if(dexFile.size<=2)
			return false;

		return true;
	};
}
