import {xu} from "xu";
import {Program} from "../../Program.js";

export class antixls extends Program
{
	website    = "https://packages.gentoo.org/packages/app-text/antixls";
	package    = "app-text/antixls";
	bin        = "antixls";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.txt")});
	renameOut  = true;
	verify     = (r, dexFile) =>
	{
		if(dexFile.size>xu.MB*25)
			return true;

		if(r.stderr.toLowerCase().includes("encrypted documents are not supported"))
		{
			r.meta.passwordProtected = true;
			return false;
		}

		if(dexFile.size<=12)
			return false;

		return true;
	};
}
