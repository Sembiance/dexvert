import {Program} from "../../Program.js";

export class joinAsGIF extends Program
{
	website = "https://www.imagemagick.org/";
	package = "media-gfx/imagemagick";
	flags   = {
		delay : "Amount of delay between GIF frames. Default: 12"
	};

	bin       = "convert";
	args      = async r => ["-strip", "-delay", `${r.flags.delay || 12}`, "-loop", "0", "-dispose", "previous", ...r.inFiles(), await r.outFile("out.gif")];
	renameOut = true;
}
