import {Format} from "../../Format.js";

export class eggPaint extends Format
{
	name       = "EggPaint / True Colour Picture";
	website    = "http://fileformats.archiveteam.org/wiki/EggPaint";
	ext        = [".trp"];
	magic      = ["EggPaint bitmap", "True Colour Picture bitmap", "deark: eggpaint", "Egg Paint :trup:", /^fmt\/(1604|1607)( |$)/];
	converters = ["deark[module:eggpaint]", "wuimg[format:eggpaint]", "wuimg[format:trp]", "recoil2png[format:TRP]", "nconvert[format:trup]"];
}
