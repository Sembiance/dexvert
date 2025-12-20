import {xu} from "xu";
import {Program} from "../../Program.js";

export class qpdf extends Program
{
	website = "https://qpdf.sourceforge.net/";
	package = "app-text/qpdf";
	flags   = {
		pages : `An argument on how to modify pages. For example, to remove the first page pass: 2-z`
	};
	bin       = "qpdf";
	args      = async r => ["--empty", ...(r.flags.pages ? ["--pages", r.inFile(), r.flags.pages, "--"] : []), await r.outFile("out.pdf")];
	renameOut = true;
}
