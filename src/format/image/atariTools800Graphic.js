import {Format} from "../../Format.js";

export class atariTools800Graphic extends Format
{
	name       = "AtariTools-800 Graphic";
	website    = "http://fileformats.archiveteam.org/wiki/AtariTools-800";
	ext        = [".agp"];
	fileSize   = 7690;
	converters = ["recoil2png"]
}
