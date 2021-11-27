import {Format} from "../../Format.js";

export class mcs extends Format
{
	name       = "Atari MCS";
	website    = "http://fileformats.archiveteam.org/wiki/MCS";
	ext        = [".mcs"];
	fileSize   = 10185;
	converters = ["recoil2png"]
}
