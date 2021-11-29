import {Program} from "../../Program.js";

export class dsstoreinfo extends Program
{
	website       = "https://github.com/gehaxelt/Python-dsstore";
	gentooPackage = "app-arch/dsstoreinfo";
	bin           = "dsstoreinfo";
	args          = r => [r.inFile()];
	runOptions    = async r => ({stdoutFilePath : await r.outFile("out.txt")});
}
