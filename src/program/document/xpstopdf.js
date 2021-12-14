import {Program} from "../../Program.js";

export class xpstopdf extends Program
{
	website   = "https://wiki.gnome.org/Projects/libgxps";
	package   = "app-text/libgxps";
	bin       = "xpstopdf";
	args      = async r => [r.inFile(), await r.outFile("out.pdf")];
	renameOut = true;
}
