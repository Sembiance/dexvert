import {Format} from "../../Format.js";

export class ags extends Format
{
	name       = "Atari Graphics Studio";
	website    = "http://g2f.atari8.info/";
	ext        = [".ags"];
	magic      = ["Atari Graphics Studio bitmap"];
	converters = ["recoil2png"]
}
