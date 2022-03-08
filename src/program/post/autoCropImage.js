import {Program} from "../../Program.js";

export class autoCropImage extends Program
{
	website = "https://www.imagemagick.org/";
	package = "media-gfx/imagemagick";
	flags   = {
		fuzzPercentage : `What level of percentage to allow for fuzz. Default: 20`,
		borderColor    : `What border color to use. Default #FFFFFF`
	};

	bin       = "convert";
	args      = async r => [r.inFile(), "-bordercolor", r.flags.borderColor ?? "#FFFFFF", "-border", "1x1", "-fuzz", `${r.flags.fuzzPercentage || 20}%`, "-trim", "+repage", await r.outFile("out.png")];
	renameOut = true;
}
