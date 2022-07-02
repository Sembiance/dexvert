import {Program} from "../../Program.js";

export class pxview extends Program
{
	website    = "https://sourceforge.net/projects/pxlib/files/pxview/";
	package    = "dev-db/pxview";
	bin        = "pxview";
	args       = r => ["--csv", r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.csv")});
	renameOut  = true;
}
