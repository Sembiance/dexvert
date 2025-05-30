import {Format} from "../../Format.js";

export class msp extends Format
{
	name       = "Microsoft Paint";
	website    = "http://fileformats.archiveteam.org/wiki/MSP_(Microsoft_Paint)";
	ext        = [".msp"];
	magic      = ["Microsoft Paint bitmap", /^M?icrosoft Paint image data/, "Microsoft Paint (MSP)) (msp)", "deark: msp (MS Paint", /^fmt\/912( |$)/, /^x-fmt\/214( |$)/];
	converters = ["recoil2png", "deark[module:msp]", "nconvert", "ffmpeg[format:msp][outType:png]", "hiJaakExpress", "pv[matchType:magic]"];
}
