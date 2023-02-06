import {xu} from "xu";
import {Program} from "../../Program.js";

export class mrsiddecode extends Program
{
	website   = "https://www.extensis.com/support/developers";
	bin       = Program.binPath("mrSID/mrsiddecode");
	args      = async r => ["-inputFile", r.inFile(), "-outputFile", await r.outFile("out.tiff")];
	renameOut = true;
	chain     = "convert[removeAlpha]";
}
