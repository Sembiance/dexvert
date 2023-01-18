import {Program} from "../../Program.js";

export class pdb2csv extends Program
{
	website    = "https://sourceforge.net/projects/palm-db-tools/";
	package    = "dev-db/palm-db-tools";
	bin        = "pdb2csv";
	args       = r => [r.inFile({absolute : true})];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.csv")});
	renameOut  = true;
}
