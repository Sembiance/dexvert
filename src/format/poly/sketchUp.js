import {Format} from "../../Format.js";

export class sketchUp extends Format
{
	name       = "SketchUp Model";
	website    = "http://fileformats.archiveteam.org/wiki/SKP";
	ext        = [".skp"];
	magic      = ["SketchUp Model", "SketchUp model", /^fmt\/(1265|1266)( |$)/];
	converters = ["nconvert"];
}
