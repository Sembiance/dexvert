import {xu} from "xu";
import {Program} from "../../Program.js";

export class psiconv extends Program
{
	website    = "https://frodo.looijaard.name/project/psiconv";
	package    = "app-text/psiconv";
	flags   = {
		outType     : "Which format to convert into. Run `psiconv --help` for a list. Default: HTML4"
	};

	bin        = "psiconv";
	args       = r => [`--type=${r.flags.outType || "HTML4"}`, r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile(`out.${(r.flags.outType || "HTML4")==="ASCII" ? "txt" : "html"}`)});
	verify     = (r, dexFile) => dexFile.size>xu.KB;
	renameOut  = true;
}
