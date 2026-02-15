import {Format} from "../../Format.js";

export class int95a extends Format
{
	name       = "INT95a";
	website    = "http://fileformats.archiveteam.org/wiki/INT95a";
	ext        = [".int"];
	magic      = ["Atari INT95a bitmap"];
	converters = ["recoil2png[format:INT.Int]"];
}
