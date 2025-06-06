import {Format} from "../../Format.js";

export class spectrum512C extends Format
{
	name       = "Spectrum 512 Compressed";
	website    = "http://fileformats.archiveteam.org/wiki/Spectrum_512_formats";
	ext        = [".spc"];
	mimeType   = "image/x-spectrum512-compressed";
	magic      = ["Spectrum 512 compressed", "deark: spectrum512c (Spectrum 512 Compressed)", "Spectrum 512 (Compressed) :spc:"];
	converters = ["deark[module:spectrum512c]", "recoil2png", "nconvert[format:spc]"];
}
