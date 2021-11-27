import {Format} from "../../Format.js";

export class hvif extends Format
{
	name       = "Haiku Vector Icon Format";
	website    = "http://fileformats.archiveteam.org/wiki/Haiku_Vector_Icon_Format";
	ext        = [".hvif"];
	mimeType   = "image/x-hvif";
	magic      = ["Haiku Vector Icon Format"];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
