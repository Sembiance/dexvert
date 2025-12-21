import {Program} from "../../Program.js";

export class tr extends Program
{
	website = "https://www.gnu.org/software/coreutils/";
	package = "sys-apps/coreutils";
	flags   = {
		ext    : "Ensure the output file has a specific extension",
		delete : "Which characters to delete"
	};
	bin        = "tr";
	args       = r => (r.flags.delete ? [`-d`, r.flags.delete] : []);
	runOptions = async r => ({stdinFilePath : r.inFile({absolute : true}), stdoutFilePath : await r.outFile(`outfile${r.flags.ext || ""}`)});
	renameOut  = true;
}
