import {Format} from "../../Format.js";

export class gunpaint extends Format
{
	name       = "Gunpaint";
	website    = "http://fileformats.archiveteam.org/wiki/Gunpaint";
	ext        = [".gun", ".ifl"];
	fileSize   = 33603;
	byteCheck  = [{offset : 0, match : [0x00, 0x40]}];
	converters = ["recoil2png", "view64"];
}
