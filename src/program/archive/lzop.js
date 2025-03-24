import {Program} from "../../Program.js";

export class lzop extends Program
{
	website   = "https://www.lzop.org/";
	package   = "app-arch/lzop";
	bin       = "lzop";
	args      = async r => ["-d", "-o", await r.outFile("out"), r.inFile()];
	renameOut = true;
}
