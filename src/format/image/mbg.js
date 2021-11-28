import {Format} from "../../Format.js";

export class mbg extends Format
{
	name       = "Mad Designer";
	website    = "http://fileformats.archiveteam.org/wiki/Mad_Designer";
	ext        = [".mbg"];
	fileSize   = 16384;
	converters = ["recoil2png"];
}
