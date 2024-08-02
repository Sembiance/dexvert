import {Format} from "../../Format.js";

export class eggPaint extends Format
{
	name       = "EggPaint / True Colour Picture";
	website    = "http://fileformats.archiveteam.org/wiki/EggPaint";
	ext        = [".trp"];
	magic      = ["EggPaint bitmap", "True Colour Picture bitmap", /^fmt\/(1604|1607)( |$)/];
	converters = ["deark[module:eggpaint]", "recoil2png"];
}
