import {Format} from "../../Format.js";

export class gimpBrush extends Format
{
	name       = "GIMP Brush";
	website    = "http://fileformats.archiveteam.org/wiki/GIMP_Brush";
	ext        = [".gbr", ".gpb"];
	magic      = ["GIMP Brush", "GIMP brush data", "image/x-gimp-gbr"];
	converters = ["gimp", "nconvert"];
}
