import {Format} from "../../Format.js";

export class sketchPaddles extends Format
{
	name       = "Sketch-PadDles";
	website    = "http://fileformats.archiveteam.org/wiki/Sketch-PadDles";
	ext        = [".skp"];
	converters = ["recoil2png[format:SKP]"];
}
