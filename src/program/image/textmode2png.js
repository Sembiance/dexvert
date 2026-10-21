import {xu} from "xu";
import {Program} from "../../Program.js";

export class textmode2png extends Program
{
	website = "https://metacpan.org/dist/Image-TextMode";
	package = "media-gfx/Image-TextMode";
	flags   = {
		format : "Specify the input format type. REQUIRED. See list in programsFormats.txt"
	};
	bin       = "textmode2png";
	args      = async r => ["-if", r.flags.format, "-o", await r.outFile("out.png"), r.inFile()];
	renameOut = true;
}
