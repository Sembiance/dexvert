import {Format} from "../../Format.js";

export class god extends Format
{
	name       = "GodPaint";
	website    = "http://fileformats.archiveteam.org/wiki/GodPaint";
	ext        = [".god"];
	magic      = ["deark: godpaint"];
	fileSize   = 153_606;
	converters = ["deark[module:godpaint]", "wuimg[format:god][hasExtMatch]", "recoil2png"];
	verify     = ({meta}) => meta.width<2000 && meta.height<2000;
}
