import {Program} from "../../Program.js";
import {fileUtil, runUtil} from "xutil";

export class dblatex extends Program
{
	website = "http://dblatex.sourceforge.net/";
	package = "app-text/dblatex";
	flags   = {
		format : "Which output format to generate. For list run `dblatex --help` Default: pdf"
	};
	bin  = "dblatex";
	args = async r =>
	{
		r.doxBookTmpPath = await fileUtil.genTempPath(undefined, ".xml");
		// some files (such as AmigaChannel5.xml) have invalid XML entity codes in them (search for reseÏa  dir) produced by grotag. So we filter out the hex entities entirely to be safe
		await runUtil.run("sed", ["-e", "s/&#[A-Za-z0-9]\\+;//g", r.inFile()], {cwd : r.f.root, stdoutEncoding : "binary", stdoutFilePath : r.doxBookTmpPath});
		return ["--quiet", `--type=${r.flags.format || "pdf"}`, "-o", await r.outFile("out.pdf"), r.doxBookTmpPath];
	};
	postExec  = async r => await fileUtil.unlink(r.doxBookTmpPath, {recursive : true});
	renameOut = true;
}
