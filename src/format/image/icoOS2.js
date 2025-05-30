import {Format} from "../../Format.js";

export class icoOS2 extends Format
{
	name       = "OS/2 Icon File";
	website    = "http://fileformats.archiveteam.org/wiki/OS/2_Icon";
	ext        = [".ico"];
	magic      = ["OS/2 icon", "OS/2 graphic array", "OS/2 Bitmap Graphics Array", "Bitmap Bild (Typ 2", "deark: os2bmp (OS/2 Icon)", "deark: os2bmp (OS/2 Color Icon)", /^OS\/2 [12].x color icon/];
	converters = ["deark[module:os2bmp]"];
}
