import {Format} from "../../Format.js";

export class rp extends Format
{
	name       = "Rainbow Painter";
	website    = "http://fileformats.archiveteam.org/wiki/Rainbow_Painter";
	ext        = [".rp"];
	fileSize   = 10242;
	converters = ["recoil2png", "nconvert", "view64"];
}
