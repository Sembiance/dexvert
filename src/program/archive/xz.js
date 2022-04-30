import {Program} from "../../Program.js";

export class xz extends Program
{
	website    = "https://tukaani.org/xz/";
	package    = "app-arch/xz-utils";
	bin        = "xz";
	args       = r => ["--decompress", "--stdout", r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out")});
	renameOut  = true;
}
