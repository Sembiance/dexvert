import {Program} from "../../Program.js";

export class dsstoreinfo extends Program
{
	website    = "https://github.com/gehaxelt/Python-dsstore";
	package    = "app-arch/dsstoreinfo";
	bin        = "dsstoreinfo";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.txt")});
	renameOut  = true;
}
