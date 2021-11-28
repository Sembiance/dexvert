import {Format} from "../../Format.js";

export class god extends Format
{
	name       = "GodPaint";
	website    = "http://fileformats.archiveteam.org/wiki/GodPaint";
	ext        = [".god"];
	fileSize   = 153_606;
	converters = ["recoil2png"];
}
