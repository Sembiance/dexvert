import {Format} from "../../Format.js";

export class sar extends Format
{
	name       = "Saracen Paint";
	website    = "http://fileformats.archiveteam.org/wiki/Saracen_Paint";
	ext        = [".sar"];
	mimeType   = "image/x-saracen-paint";
	magic      = ["Saracen Paint Image", "Saracen Paint :sar:"];
	weakMagic  = true;
	converters = ["nconvert[format:sar]", "recoil2png", `abydosconvert[format:${this.mimeType}]`, "view64[matchType:magic]"];
}
