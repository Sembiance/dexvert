import {Format} from "../../Format.js";

export class eza extends Format
{
	name       = "EZ-Art Professional";
	website    = "http://fileformats.archiveteam.org/wiki/EZ-Art_Professional";
	ext        = [".eza"];
	magic      = ["EZ-Art Professional bitmap"];
	converters = ["recoil2png[format:EZA]", "wuimg[format:ez]"];
}
