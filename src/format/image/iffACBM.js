import {Format} from "../../Format.js";

export class iffACBM extends Format
{
	name       = "IFF Amiga Contiguous Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/ILBM#ACBM";
	ext        = [".lbm", ".ilbm", ".iff", ".acbm"];
	magic      = ["IFF data, ACBM continuous image", "IFF Amiga Contiguous BitMap"];
	converters = ["recoil2png"]
}
