import {Program} from "../../Program.js";

export class joinAsGIF extends Program
{
	website = "https://www.imagemagick.org/";
	package = "media-gfx/imagemagick";
	flags   = {
		frameDelay : "Amount of delay between GIF frames. Default: 12"
	};

	bin       = "magick";
	args      = async r => ["-strip", "-delay", `${r.flags.frameDelay || 12}`, "-loop", "0", "-dispose", "previous", ...r.inFiles(), await r.outFile("out.gif")];
	renameOut = true;
}
