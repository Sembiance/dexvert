import {xu} from "xu";
import {Program} from "../../Program.js";

export class rotateImage extends Program
{
	website = "https://www.imagemagick.org/";
	package = "media-gfx/imagemagick";
	flags   = {
		degrees : "Specify the number of degrees to rotate the image"
	};

	bin        = "magick";
	args       = async r => [r.inFile(), "-rotate", r.flags.degrees, await r.outFile("out.png")];
	runOptions = {limitRAM : xu.GB*3};
	renameOut  = true;
}
