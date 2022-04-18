import {Format} from "../../Format.js";

export class pixelPerfect extends Format
{
	name        = "Pixel Perfect";
	website     = "http://fileformats.archiveteam.org/wiki/Pixel_Perfect";
	ext         = [".pp", ".ppp"];
	unsupported = true;
	notes       = "Can't reliably detect this format and recoil2png & view64 will convert almost any file you give it into garbage";
	converters  = ["recoil2png", "view64"];
}
