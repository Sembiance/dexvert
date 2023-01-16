import {Format} from "../../Format.js";

export class arArchive extends Format
{
	name        = "AR Archive";
	website     = "http://fileformats.archiveteam.org/wiki/AR";
	ext         = [".a", ".lib"];
	magic       = ["current ar archive", "ar archive", /^archive$/];
	unsupported = true;
	notes       = "We used to convert with deark/ar but all that usually is stored inside is .o object which are not interesting and some .a files like libphobos2.a produce 9,999 files which is a lot of noise.";
	//converters = ["deark", "ar"];
}
