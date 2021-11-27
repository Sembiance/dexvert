import {Format} from "../../Format.js";

export class gemViewDither extends Format
{
	name       = "GEM-View Dither";
	website    = "https://www.atariuptodate.de/en/768/gem-view";
	ext        = [".dit"];
	fileSize   = 266;
	magic      = ["GEM-View Dither"];
	converters = ["nconvert"]
}
