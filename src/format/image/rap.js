import {Format} from "../../Format.js";

export class rap extends Format
{
	name       = "Vidig Paint";
	website    = "http://fileformats.archiveteam.org/wiki/Vidig_Paint";
	ext        = [".rap"];
	fileSize   = 7681;
	converters = ["recoil2png[format:RAP]"];
}
