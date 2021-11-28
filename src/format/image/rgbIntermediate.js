import {Format} from "../../Format.js";

export class rgbIntermediate extends Format
{
	name       = "Atari RGB Intermediate";
	ext        = [".rgb"];
	mimeType   = "image/x-atari-rgb-intermediate";
	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`];
}
