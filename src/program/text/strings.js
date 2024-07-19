import {Program} from "../../Program.js";

export class strings extends Program
{
	website    = "https://www.gnu.org/software/binutils/";
	package    = "sys-devel/binutils";
	flags   = {
		minBytes     : "Minimum number of bytes for a word to be extracted. Default: 5"
	};
	bin            = "strings";
	unsafe         = true;
	allowDupOut    = true;	// if strings happens to produce a file identical to the original, then that means it's 100% text and that's totally fine to allow
	forbidChildRun = true;
	args           = r => ["--all", `--bytes=${r.flags.minBytes || 5}`, r.inFile()];
	runOptions     = async r => ({stdoutFilePath : await r.outFile("out.txt")});
	renameOut      = true;
}
