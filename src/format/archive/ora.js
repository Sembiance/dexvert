import {Format} from "../../Format.js";

export class ora extends Format
{
	name       = "OpenRaster";
	website    = "http://fileformats.archiveteam.org/wiki/OpenRaster";
	ext        = [".ora"];
	mimeType   = "image/openraster";
	magic      = ["OpenRaster Image Format", "OpenRaster bitmap"];
	converters = ["deark"];
}
