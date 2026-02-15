import {Format} from "../../Format.js";

export class indyPaint extends Format
{
	name       = "IndyPaint";
	website    = "http://fileformats.archiveteam.org/wiki/IndyPaint";
	ext        = [".tru"];
	magic      = ["IndyPaint bitmap", "deark: indypaint"];
	converters = ["deark[module:indypaint]", "wuimg[format:indy]", "recoil2png[format:TRU,HGR]"];
}
