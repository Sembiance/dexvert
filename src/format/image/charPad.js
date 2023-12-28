import {Format} from "../../Format.js";

export class charPad extends Format
{
	name       = "CharPad";
	website    = "http://fileformats.archiveteam.org/wiki/CharPad";
	ext        = [".ctm"];
	magic      = ["CharPad"];
	converters = ["recoil2png", "view64"];
}
