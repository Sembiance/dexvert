import {Format} from "../../Format.js";

export class gemFont extends Format
{
	name       = "GEM Bitmap Font";
	website    = "http://fileformats.archiveteam.org/wiki/GEM_bitmap_font";
	ext        = [".gft", ".fnt"];
	magic      = ["GEM GDOS font", "deark: gemfont"];
	converters = ["deark[module:gemfont]"];
}
