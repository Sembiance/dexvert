import {Format} from "../../Format.js";

export class zx3 extends Format
{
	name       = "ZX Spectrum - Tricolor RGB";
	website    = "http://fileformats.archiveteam.org/wiki/Tricolor_RGB";
	ext        = [".3"];
	mimeType   = "image/x-tricolor-rgb";
	fileSize   = 18432;
	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`];
}
