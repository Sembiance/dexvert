import {Format} from "../../Format.js";

export class ags extends Format
{
	name       = "Atari Graphics Studio";
	website    = "http://fileformats.archiveteam.org/wiki/Atari_Graphics_Studio";
	ext        = [".ags"];
	magic      = ["Atari Graphics Studio bitmap"];
	converters = ["recoil2png[format:AGS]"];
}
