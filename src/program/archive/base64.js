import {Program} from "../../Program.js";

export class base64 extends Program
{
	website    = "https://www.gnu.org/software/coreutils/";
	package    = "sys-apps/coreutils";
	bin        = "base64";
	args       = r => ["-i", "-d", r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("outfile")});
	renameOut  = true;
}
