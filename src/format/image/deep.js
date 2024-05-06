import {Format} from "../../Format.js";

export class deep extends Format
{
	name       = "IFF-DEEP";
	website    = "http://fileformats.archiveteam.org/wiki/IFF-DEEP";
	ext        = [".deep"];
	magic      = ["IFF DEEP animation/bitmap", "IFF data, DEEP"];
	converters = ["recoil2png", "deark[module:deep]", "ffmpeg[outType:png]", "iff_convert"];
}
