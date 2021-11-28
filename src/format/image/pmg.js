import {Format} from "../../Format.js";

export class pmg extends Format
{
	name       = "Paint Magic";
	website    = "http://fileformats.archiveteam.org/wiki/Paint_Magic";
	ext        = [".pmg"];
	converters = ["recoil2png", "view64"];
}
