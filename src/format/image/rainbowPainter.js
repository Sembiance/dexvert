import {Format} from "../../Format.js";

export class rainbowPainter extends Format
{
	name       = "Rainbow Painter";
	website    = "http://fileformats.archiveteam.org/wiki/Rainbow_Painter";
	ext        = [".rp"];
	magic      = ["Rainbow Painter :rp:"];
	fileSize   = 10242;
	converters = ["recoil2png[format:RP]", "nconvert[format:rp]", "view64"];
}
