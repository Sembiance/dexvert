import {Format} from "../../Format.js";

export class amigaBitmapFontContent extends Format
{
	name       = "Amiga Bitmap Font Content";
	website    = "http://fileformats.archiveteam.org/wiki/Amiga_bitmap_font";
	magic      = ["amigaBitmapFontContent"];
	converters = ["amigaBitmapFontContentToOTF"];
}
