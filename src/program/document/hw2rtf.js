import {Program} from "../../Program.js";
import {path} from "std";

export class hw2rtf extends Program
{
	website   = "https://github.com/Sembiance/dexvert/";
	bin       = "python3";
	args      = async r => [path.join(Program.binPath("hw2rtf"), "hw2rtf.py"), r.inFile(), await r.outFile("out.rtf")];
	chain     = "soffice[format:Rich Text Format]";
	renameOut = true;
}
