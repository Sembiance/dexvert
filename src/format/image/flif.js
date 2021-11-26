import {Format} from "../../Format.js";

export class flif extends Format
{
	name       = "Free Lossless Image Format";
	website    = "http://fileformats.archiveteam.org/wiki/FLIF";
	ext        = [".flif"];
	mimeType   = "image/x-flif";
	magic      = ["Free Lossless Image Format", "FLIF"];
	converters = [`abydosconvert[format:${this.mimeType}]`]
}
