import {Program} from "../../Program.js";

export class ddjvu extends Program
{
	website = "http://djvu.sourceforge.net/";
	package = "app-text/djvu";
	flags   = {
		outType  : `Which type to convert to (pdf || png). Default: pdf`
	};

	bin        = "ddjvu";
	args       = async r => [`-format=${r.flags.outType==="png" ? "pnm" : (r.flags.outType || "pdf")}`, r.inFile(), await r.outFile(`out.${r.flags.outType==="png" ? "pnm" : (r.flags.outType || "pdf")}`)];
	renameOut  = true;
	chain      = "?convert";
	chainCheck = r => r.flags.outType==="png";
}
