import {Format} from "../../Format.js";

export class kyssKYG extends Format
{
	name       = "Kyss KYG";
	website    = "http://fileformats.archiveteam.org/wiki/KYG";
	ext        = [".kyg"];
	magic      = ["KYG bitmap"];
	mimeType   = "image/x-kyss-graphics";
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
