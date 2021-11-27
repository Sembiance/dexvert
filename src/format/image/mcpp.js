import {Format} from "../../Format.js";

export class mcpp extends Format
{
	name       = "Paradox";
	website    = "http://fileformats.archiveteam.org/wiki/Paradox";
	ext        = [".mcpp"];
	fileSize   = 8008;
	converters = ["recoil2png"]
}
