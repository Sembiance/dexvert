import {Format} from "../../Format.js";

export class fwa extends Format
{
	name       = "Fun With Art";
	website    = "http://fileformats.archiveteam.org/wiki/Fun_with_Art";
	ext        = [".fwa"];
	converters = ["recoil2png[format:FWA]"];
}
