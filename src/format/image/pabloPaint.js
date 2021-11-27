import {Format} from "../../Format.js";

export class pabloPaint extends Format
{
	name       = "PabloPaint";
	website    = "http://fileformats.archiveteam.org/wiki/PabloPaint";
	ext        = [".pa3", ".ppp"];
	mimeType   = "image/x-pablo-packed-picture";
	magic      = ["PabloPaint packed bitmap"];
	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`]
}
