import {Format} from "../../Format.js";

export class ged extends Format
{
	name       = "GED";
	website    = "http://fileformats.archiveteam.org/wiki/GED";
	ext        = [".ged"];
	magic      = ["Atari GED bitmap"];
	converters = ["recoil2png[format:GED]"];
}
