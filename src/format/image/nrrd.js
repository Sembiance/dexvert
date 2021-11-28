import {Format} from "../../Format.js";

export class nrrd extends Format
{
	name       = "Nearly Raw Raster Data";
	website    = "http://teem.sourceforge.net/nrrd/format.html";
	ext        = [".nrrd"];
	magic      = ["Nearly Raw Raster Data"];
	mimeType   = "image/x-nrrd";
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
