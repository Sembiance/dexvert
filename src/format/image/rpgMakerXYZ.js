import {Format} from "../../Format.js";

export class rpgMakerXYZ extends Format
{
	name       = "RPG Maker XYZ Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/XYZ_(RPG_Maker)";
	ext        = [".xyz"];
	magic      = ["XYZ Graphics bitmap", "RM2k XYZ Graphics Format :xyz:"];
	converters = ["xyz2png", "wuimg[format:xyz]", "nconvert[format:xyz]"];
}
