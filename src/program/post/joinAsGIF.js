import {xu} from "xu";
import {Program} from "../../Program.js";

export class joinAsGIF extends Program
{
	website = "https://www.imagemagick.org/";
	package = "media-gfx/imagemagick";
	flags   = {
		frameDelay : "Amount of delay between GIF frames. Default: 12",
		outType    : "Output type. Default: gif"
	};

	bin       = "magick";
	args      = async r => ["-delay", `${r.flags.frameDelay || 12}`, "-dispose", "previous", ...r.inFiles(), "-loop", "0", "-strip", await r.outFile(`out.${r.flags.outType || "gif"}`)];
	renameOut = true;
}
