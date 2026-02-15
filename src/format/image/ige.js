import {Format} from "../../Format.js";

export class ige extends Format
{
	name       = "Interlace Graphics Editor";
	website    = "http://fileformats.archiveteam.org/wiki/Interlace_Graphics_Editor";
	ext        = [".ige"];
	converters = ["recoil2png[format:IGE]"];
}
