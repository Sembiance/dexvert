import {Program} from "../../Program.js";

export class sed extends Program
{
	website = "https://www.gnu.org/software/sed/";
	package = "sys-apps/sed";
	flags   = {
		ext : "Ensure the output file has a specific extension",
		op   : "What to operation to perform"
	};
	bin        = "sed";
	unsafe     = true;
	args       = r => [r.flags.op, r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile(`out${r.flags.ext || ""}`)});
	renameOut  = true;
}
