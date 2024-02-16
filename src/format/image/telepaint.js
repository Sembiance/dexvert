import {Format} from "../../Format.js";

export class telepaint extends Format
{
	name        = "Telepaint";
	website     = "http://fileformats.archiveteam.org/wiki/TelePaint/Splash_graphics";
	ext         = [".ss", ".st"];
	magic       = ["Telepaint canvas/stamp bitmap"];
	converters  = ["telepaintConvert"];
}
