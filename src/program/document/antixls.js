import {Program} from "../../Program.js";

export class antixls extends Program
{
	website    = "https://packages.gentoo.org/packages/app-text/antixls";
	package    = "app-text/antixls";
	bin        = "antixls";
	args       = r => [r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.txt")});
	renameOut  = true;
}
