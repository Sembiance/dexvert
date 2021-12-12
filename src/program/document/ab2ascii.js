import {Program} from "../../Program.js";

export class ab2ascii extends Program
{
	website   = "http://aminet.net/package/dev/misc/ab2ascii-1.3";
	package   = "dev-lang/ab2ascii";
	unsafe    = true;
	bin       = "ab2ascii";
	args      = async r => ["-o", await r.outFile("out.txt"), r.inFile()];
	renameOut = true;
}
