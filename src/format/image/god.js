import {Format} from "../../Format.js";

export class god extends Format
{
	name       = "GodPaint";
	website    = "http://fileformats.archiveteam.org/wiki/GodPaint";
	ext        = [".god"];
	magic      = ["deark: godpaint"];
	fileSize   = 153_606;
	converters = ["deark[module:godpaint]", "wuimg[hasExtMatch]", "recoil2png"];
}
