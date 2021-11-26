import {Format} from "../../Format.js";

export class eggPaint extends Format
{
	name       = "EggPaint / True Colour Picture";
	website    = "http://fileformats.archiveteam.org/wiki/EggPaint";
	ext        = [".trp"];
	magic      = ["EggPaint bitmap", "True Colour Picture bitmap"];
	converters = ["recoil2png"]
}
