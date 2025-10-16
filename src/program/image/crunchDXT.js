import {xu} from "xu";
import {Program} from "../../Program.js";

export class crunchDXT extends Program
{
	website   = "https://github.com/BinomialLLC/crunch";
	bin       = Program.binPath("crunchDXT");
	args      = async r => ["-file", r.inFile(), "-out", await r.outFile("out.tga")];
	renameOut = true;
	chain     = "deark[module:tga][matchType:magic][opt:tga:trans=1]";
}
