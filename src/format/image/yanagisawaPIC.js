import {Format} from "../../Format.js";

export class yanagisawaPIC extends Format
{
	name       = "Yanagisawa PIC";
	website    = "http://fileformats.archiveteam.org/wiki/PIC_(Yanagisawa)";
	ext        = [".pic"];
	magic      = ["Yanagisawa PIC image file", "PIC bitmap"];
	weakMagic  = true;
	converters = ["recoil2png"];
}
