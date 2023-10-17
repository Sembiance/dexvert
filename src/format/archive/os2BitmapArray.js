import {Format} from "../../Format.js";

export class os2BitmapArray extends Format
{
	name       = "OS/2 Bitmap Array";
	website    = "http://fileformats.archiveteam.org/wiki/OS/2_Bitmap_Array";
	magic      = ["OS/2 graphic array", "OS/2 Bitmap Graphics Array"];
	ext        = [".bga", ".bmp", ".ico"];
	weakExt    = [".bmp", ".ico"];
	converters = ["deark[module:os2bmp]"];
}
