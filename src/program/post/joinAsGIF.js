import {Program} from "../../Program.js";

export class joinAsGIF extends Program
{
	website        = "https://www.imagemagick.org/";
	gentooPackage  = "media-gfx/imagemagick";
	gentooUseFlags = "X bzip2 cxx fontconfig fpx heif jbig jpeg jpeg2k lzma openmp png postscript svg tiff truetype webp wmf xml zlib";
	flags = {
		delay : "Amount of delay between GIF frames. Default: 12"
	};

	bin  = "convert";
	args = async r => ["-strip", "-delay", `${r.flags.delay || 12}`, "-loop", "0", "-dispose", "previous", ...r.inFiles(), await r.outFile("out.gif")];
}
