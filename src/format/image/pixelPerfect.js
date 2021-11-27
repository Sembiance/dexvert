import {Format} from "../../Format.js";

export class pixelPerfect extends Format
{
	name       = "Pixel Perfect";
	website    = "http://fileformats.archiveteam.org/wiki/Pixel_Perfect";
	ext        = [".pp", ".ppp"];
	converters = ["recoil2png", "view64"]
}
