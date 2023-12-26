import {Program} from "../../Program.js";

export class iio2png extends Program
{
	website   = "http://github.com/Sembiance/iio2png/";
	package   = "media-gfx/iio2png";
	bin       = "iio2png";
	args      = r => [r.inFile({absolute : true}), r.outDir({absolute : true})];
	renameOut = true;
}
