import {Format} from "../../Format.js";

export class all extends Format
{
	name       = "Atari Graph Image";
	website    = "http://fileformats.archiveteam.org/wiki/Graph";
	ext        = [".all"];
	converters = ["recoil2png[format:ALL]"];
}
