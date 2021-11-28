import {Format} from "../../Format.js";

export class drazPaint extends Format
{
	name       = "Draz Paint";
	website    = "http://fileformats.archiveteam.org/wiki/Drazpaint";
	ext        = [".drz", ".drp"];
	mimeType   = "image/x-draz-paint";
	magic      = ["Drazpaint"];
	weakMagic  = true;
	converters = ["nconvert", "recoil2png", `abydosconvert[format:${this.mimeType}]`, "view64"];
}
