import {Program} from "../../Program.js";

export class gfalist extends Program
{
	website    = "https://github.com/Sembiance/gfalist";
	package    = "dev-lang/gfalist";
	bin        = "gfalist";
	args       = r => ["-f", r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.bas")});
	renameOut  = true;
}
