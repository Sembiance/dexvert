import {Program} from "../../Program.js";

export class mozlz4 extends Program
{
	website   = "https://github.com/jusw85/mozlz4";
	bin       = Program.binPath("mozlz4");
	args      = async r => [r.inFile(), await r.outFile("outfile")];
	renameOut = true;
}
