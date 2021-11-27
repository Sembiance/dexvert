import {Program} from "../../Program.js";

export class gd2topng extends Program
{
	website        = "https://libgd.org";
	gentooPackage  = "media-libs/gd";
	gentooUseFlags = "fontconfig jpeg png tiff truetype webp xpm zlib";
	bin            = "gd2topng"
	args           = async r => [r.inFile(), await r.outFile("out.png")];
}
