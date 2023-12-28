import {Format} from "../../Format.js";

export class gemViewDither extends Format
{
	name       = "GEM-View Dither";
	website    = "http://fileformats.archiveteam.org/wiki/GEM-View_Dither";
	ext        = [".dit"];
	fileSize   = 266;
	magic      = ["GEM-View Dither"];
	converters = ["nconvert"];
}
