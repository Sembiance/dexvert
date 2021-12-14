import {Program} from "../../Program.js";

export class texi2pdf extends Program
{
	website   = "https://www.gnu.org/software/texinfo/";
	package   = "sys-apps/texinfo";
	notes     = "Fails on most sample texInfo files I give it";
	bin       = "texi2pdf";
	args      = async r => ["--pdf", "--clean", `--output=${await r.outFile("out.pdf")}`, r.inFile()];
	renameOut = true;
}
