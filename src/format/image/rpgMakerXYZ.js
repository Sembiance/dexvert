import {Format} from "../../Format.js";

export class rpgMakerXYZ extends Format
{
	name       = "RPG Maker XYZ Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/XYZ_(RPG_Maker)";
	ext        = [".xyz"];
	magic      = ["XYZ Graphics bitmap"];
	converters = ["xyz2png", "nconvert"];
}
