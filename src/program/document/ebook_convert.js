import {xu} from "xu";
import {Program} from "../../Program.js";

export class ebook_convert extends Program
{
	website   = "https://calibre-ebook.com/";
	package   = "app-text/calibre-bin";
	bin       = "ebook-convert";	// man page: http://manpages.ubuntu.com/manpages/bionic/man1/ebook-convert.1.html
	args      = async r => [r.inFile(), await r.outFile("out.docx")];
	renameOut = true;
	chain     = "soffice";
}
