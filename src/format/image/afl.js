import {Format} from "../../Format.js";

export class afl extends Format
{
	name        = "AFLI-Editor Image";
	website     = "http://fileformats.archiveteam.org/wiki/AFLI-Editor";
	ext         = [".afl", ".afli"];
	unsupported = true;	// only a single sample file, somewhat "made up" extension, no specific file size and recoil+view64 will convert any .afl into a garbage output
	converters  = ["recoil2png[format:AFL]", "view64"];
}
