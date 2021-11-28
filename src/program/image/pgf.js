import {Program} from "../../Program.js";

export class pgf extends Program
{
	website       = "https://www.libpgf.org/";
	gentooPackage = "media-gfx/libpgf-tools";
	bin           = "pgf";
	args          = async r => ["-d", r.inFile(), await r.outFile("out.png")];
}
