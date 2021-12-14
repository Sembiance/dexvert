import {Program} from "../../Program.js";

export class latex2pdf extends Program
{
	website   = "http://latex2rtf.sourceforge.net/";
	package   = "dev-tex/latex2rtf";
	bin       = "latex2rtf";
	args      = async r => ["-T", r.f.root, "-o", await r.outFile("out.rtf"), r.inFile()];
	chain     = "dexvert[asFormat:document/rtf]";
	renameOut = true;
}
