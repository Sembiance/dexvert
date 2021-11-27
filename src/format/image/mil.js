import {Format} from "../../Format.js";

export class mil extends Format
{
	name       = "Micro Illustrator";
	website    = "http://fileformats.archiveteam.org/wiki/Micro_Illustrator";
	ext        = [".mil"];
	fileSize   = 10022;
	converters = ["recoil2png", "nconvert"]
}
