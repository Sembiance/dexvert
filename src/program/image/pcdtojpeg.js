import {Program} from "../../Program.js";

export class pcdtojpeg extends Program
{
	website = "https://pcdtojpeg.sourceforge.io/Home.html";
	package = "media-gfx/pcdtojpeg";
	bin     = "pcdtojpeg";
	args    = async r => ["-q", "100", r.inFile(), await r.outFile("out.jpg")];
}
