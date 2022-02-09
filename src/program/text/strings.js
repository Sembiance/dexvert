import {Program} from "../../Program.js";

export class strings extends Program
{
	website    = "https://www.gnu.org/software/binutils/";
	package    = "sys-devel/binutils";
	bin        = "strings";
	unsafe     = true;
	args       = r => ["--all", "--bytes=5", r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.txt")});
	renameOut  = true;
}
