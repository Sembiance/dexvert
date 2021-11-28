import {Format} from "../../Format.js";

export class graphicsMagicianPainter extends Format
{
	name       = "The Graphics Magician Picture Painter";
	website    = "http://fileformats.archiveteam.org/wiki/The_Graphics_Magician_Picture_Painter";
	ext        = [".spc"];
	notes      = "It's a vector format, so it would be nice to convert to SVG, but only program that I know of that can convert it is recoil2png which just produces PNG files.";
	converters = ["recoil2png"];
}
