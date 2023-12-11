import {Program} from "../../Program.js";

export class iconvert extends Program
{
	website   = "https://github.com/AcademySoftwareFoundation/OpenImageIO";
	package   = "media-libs/openimageio";
	bin       = "iconvert";
	args      = async r => ["--threads", "1", r.inFile(), await r.outFile("out.png")];
	renameOut = true;
}
