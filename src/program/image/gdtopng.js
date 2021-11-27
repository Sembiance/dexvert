import {Program} from "../../Program.js";

export class gdtopng extends Program
{
	website        = "https://libgd.org";
	gentooPackage  = "media-libs/gd";
	gentooUseFlags = "fontconfig jpeg png tiff truetype webp xpm zlib";
	unsafe         = true;
	bin            = "gdtopng";
	args           = async r => [r.inFile(), await r.outFile("out.png")];
}
