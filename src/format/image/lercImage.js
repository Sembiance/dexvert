import {Format} from "../../Format.js";

export class lercImage extends Format
{
	name       = "Limited Error Raster Compression Image";
	website    = "http://fileformats.archiveteam.org/wiki/LERC";
	ext        = [".lrc", ".lerc", ".lerc1", ".lerc2"];
	magic      = ["Lerc 1 Image", "Lerc2 bitmap", "Lerc1 compressed bitmap"];
	converters = ["wuimg"];
}
