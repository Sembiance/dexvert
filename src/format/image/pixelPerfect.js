import {Format} from "../../Format.js";

export class pixelPerfect extends Format
{
	name        = "Pixel Perfect";
	website     = "http://fileformats.archiveteam.org/wiki/Pixel_Perfect";
	ext         = [".pp", ".ppp"];
	unsupported = true;	// only have unreliable ext pmatchs and recoil2png/view64 will convert anything
	converters  = ["recoil2png[format:PP]", "view64"];
}
