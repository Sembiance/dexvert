import {Format} from "../../Format.js";

export class monoMagic extends Format
{
	name       = "Mono Magic";
	website    = "http://fileformats.archiveteam.org/wiki/Mono_Magic";
	ext        = [".mon"];
	magic      = ["Mono Magic :mon:"];
	converters = ["recoil2png", "nconvert[format:mon]"];
}
