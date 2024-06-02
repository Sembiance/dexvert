import {Format} from "../../Format.js";

export class gxlib extends Format
{
	name       = "Genus Graphics Library Compressed Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Genus_Graphics_Library";
	ext        = [".gx", ".gxl"];
	magic      = ["Genus Graphics Library", "Archive: GXL"];
	converters = ["deark[module:gxlib]", "unpcxgx"];
}
