import {Format} from "../../Format.js";

export class rgbIntermediate extends Format
{
	name       = "Atari RGB Intermediate";
	website    = "http://fileformats.archiveteam.org/wiki/RGB_Intermediate_Format";
	ext        = [".rgb"];
	mimeType   = "image/x-atari-rgb-intermediate";
	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`];
}
