import {Format} from "../../Format.js";

export class drazPaint extends Format
{
	name       = "Draz Paint";
	website    = "http://fileformats.archiveteam.org/wiki/Drazpaint";
	ext        = [".drz", ".drp"];
	mimeType   = "image/x-draz-paint";
	magic      = ["Drazpaint", "Draz Paint :drz:"];
	weakMagic  = true;
	converters = ["nconvert[format:drz]", "recoil2png[format:DRZ,DRP]", `abydosconvert[format:${this.mimeType}]`, "view64[matchType:magic]"];
}
