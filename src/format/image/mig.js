import {Format} from "../../Format.js";

export class mig extends Format
{
	name       = "MIG";
	website    = "http://fileformats.archiveteam.org/wiki/MIG";
	ext        = [".mig"];
	magic      = ["MSX compressed Image bitmap", /^fmt\/1470( |$)/];
	converters = ["recoil2png[format:MIG]"];
}
