import {Format} from "../../Format.js";

export class gimpPattern extends Format
{
	name           = "GIMP Pattern";
	website        = "http://fileformats.archiveteam.org/wiki/GIMP_Pattern";
	ext            = [".pat"];
	forbidExtMatch = true;
	magic          = ["GIMP Pattern", "GIMP pattern data", "image/x-gimp-pat"];
	converters     = ["gimp", "nconvert"];
}
