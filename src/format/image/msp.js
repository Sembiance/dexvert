import {Format} from "../../Format.js";

export class msp extends Format
{
	name       = "Microsoft Paint";
	website    = "http://fileformats.archiveteam.org/wiki/MSP_(Microsoft_Paint)";
	ext        = [".msp"];
	magic      = ["Microsoft Paint bitmap", /^M?icrosoft Paint image data/];
	converters = ["recoil2png", "deark", "nconvert", "hiJaakExpress"];
}
