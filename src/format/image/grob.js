import {Format} from "../../Format.js";

export class grob extends Format
{
	name       = "GROB Image";
	website    = "http://fileformats.archiveteam.org/wiki/GROB";
	ext        = [".grb", ".gro"];
	magic      = ["HP 48 binary - Rev D (GROB)", "HP-48 Graphic Object Bitmap", "HP-49 Graphic Object Bitmap", "HP 49 binary - Rev X (GROB)", "HP ASII GROB bitmap", "HP 49 binary (GROB)", "HP 49 series binary transfer data"];
	converters = ["nconvert", "deark[module:grob]", "recoil2png", "imageAlchemy"];
}
