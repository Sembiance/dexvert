import {Program} from "../../Program.js";

export class smaf825 extends Program
{
	website    = "https://github.com/but80/smaf825";
	package    = "media-sound/smaf825";
	bin        = "smaf825";
	args       = r => ["dump", "--json", r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.json")});
	renameOut  = true;
}
