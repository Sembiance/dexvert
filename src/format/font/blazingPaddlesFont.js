import {Format} from "../../Format.js";

export class blazingPaddlesFont extends Format
{
	name       = "Blazing Paddles - Font";
	website    = "http://fileformats.archiveteam.org/wiki/Blazing_Paddles";
	ext        = [".chr"];
	converters = ["recoil2png[format:CHR]"];
}
