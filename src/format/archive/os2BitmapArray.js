import {Format} from "../../Format.js";

export class os2BitmapArray extends Format
{
	name       = "OS/2 Bitmap Array";
	website    = "http://fileformats.archiveteam.org/wiki/OS/2_Bitmap_Array";
	ext        = [".bga", ".bmp", ".ico"];
	weakExt    = [".bmp", ".ico"];
	magic      = ["OS/2 graphic array", "OS/2 Bitmap Graphics Array", "deark: os2bmp (OS/2 Bitmap Array", "OS/2 Graphics :bga:", /^OS\/2 Bitmap$/];
	weakMagic  = ["deark: os2bmp (OS/2 Bitmap Array"];
	converters = ["deark[module:os2bmp]", "nconvert[format:bga][extractAll]"];
}
