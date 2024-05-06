import {Program} from "../../Program.js";

export class bascat extends Program
{
	website    = "https://github.com/rwtodd/bascat";
	package    = "dev-util/bascat";
	bin        = "bascat";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.bas")});
	renameOut  = true;
}
