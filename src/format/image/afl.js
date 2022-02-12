import {Format} from "../../Format.js";

export class afl extends Format
{
	name       = "AFLI-Editor Image";
	website    = "http://fileformats.archiveteam.org/wiki/AFLI-Editor";
	ext        = [".afl", ".afli"];
	converters = ["recoil2png", "view64"];
}
