import {xu} from "xu";
import {Program} from "../../Program.js";

export class unecm extends Program
{
	website   = "https://web.archive.org/web/20140330233023/http://www.neillcorlett.com/cmdpack/";
	bin       = Program.binPath("ecm");
	args      = async r => ["d", r.inFile(), await r.outFile("outfile")];
	renameOut = true;
}
