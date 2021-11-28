import {Format} from "../../Format.js";

export class mldf extends Format
{
	name       = "Mean Streets MLDF File";
	website    = "http://fileformats.archiveteam.org/wiki/MLDF";
	ext        = [".mld"];
	mimeType   = "image/x-mldf";
	magic      = ["MLDF BMHD file"];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
