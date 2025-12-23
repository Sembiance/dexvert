import {xu} from "xu";
import {Program} from "../../Program.js";

export class montage extends Program
{
	website   = "https://www.imagemagick.org/";
	package   = "media-gfx/imagemagick";
	bin       = "montage";
	flags        = {
		colCount : "Number of columns in the output image. Default is 20."
	};
	args      = async r => [...r.inFiles(), "-tile", `${Math.min(r.inFiles().length, (+(r.flags.colCount || 20)))}x${Math.ceil(r.inFiles().length/ (+(r.flags.colCount || 20)))}`, "-geometry", "+0+0", "-background", "black", await r.outFile(`out.png`)];
	renameOut = true;
}
