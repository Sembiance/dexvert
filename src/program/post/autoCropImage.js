import {Program} from "../../Program.js";

export class autoCropImage extends Program
{
	website        = "https://www.imagemagick.org/";
	gentooPackage  = "media-gfx/imagemagick";
	gentooUseFlags = "X bzip2 cxx fontconfig fpx heif jbig jpeg jpeg2k lzma openmp png postscript svg tiff truetype webp wmf xml zlib";
	flags          =
	{
		fuzzPercentage : `What level of percentage to allow for fuzz. Default: 20`
	};

	bin  = "convert";
	args = async r => [r.inFile(), "-bordercolor", "#FFFFFF", "-border", "1x1", "-fuzz", `${r.flags.fuzzPercentage || 20}%`, "-trim", "+repage", await r.outFile("out.png")]
}
