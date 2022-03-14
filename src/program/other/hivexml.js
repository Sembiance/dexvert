import {Program} from "../../Program.js";

export class hivexml extends Program
{
	website    = "https://libguestfs.org";
	package    = "app-misc/hivex";
	bin        = "hivexml";
	args       = r => ["-k", r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.xml")});
	renameOut  = true;
}
