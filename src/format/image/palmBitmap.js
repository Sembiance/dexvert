import {Format} from "../../Format.js";

export class palmBitmap extends Format
{
	name         = "Palm Bitmap";
	website      = "http://fileformats.archiveteam.org/wiki/Palm_bitmap";
	ext          = [".palm"];
	magic        = ["deark: palmbitmap"];
	metaProvider = ["image"];
	converters   = ["deark[module:palmbitmap]", "convert"];
}
