import {Program} from "../../Program.js";
import {path} from "std";

export class quickstartIcon2Farbfeld extends Program
{
	website   = "https://www.uninformativ.de/blog/postings/2024-08-27/0/POSTING-en.html";
	package   = "media-gfx/quickstartIcon2Farbfeld";
	bin       = "quickstartIcon2Farbfeld";
	args      = r => [r.inFile(), path.join(r.outDir(), "out.ff")];
	chain     = "deark[module:farbfeld]";
	renameOut = true;
}
