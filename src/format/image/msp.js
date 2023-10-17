import {Format} from "../../Format.js";

export class msp extends Format
{
	name       = "Microsoft Paint";
	website    = "http://fileformats.archiveteam.org/wiki/MSP_(Microsoft_Paint)";
	ext        = [".msp"];
	magic      = ["Microsoft Paint bitmap", /^M?icrosoft Paint image data/, /^fmt\/912( |$)/, /^x-fmt\/214( |$)/];
	converters = ["recoil2png", "deark[module:msp]", "nconvert", "hiJaakExpress", "pv[matchType:magic]"];
}
