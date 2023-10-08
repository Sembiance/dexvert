import {Format} from "../../Format.js";

export class nrrd extends Format
{
	name       = "Nearly Raw Raster Data";
	website    = "http://teem.sourceforge.net/nrrd/format.html";
	ext        = [".nrrd"];
	magic      = ["Nearly Raw Raster Data", /^fmt\/(1002|1005)( |$)/];
	mimeType   = "image/x-nrrd";
	converters = ["unu", `abydosconvert[format:${this.mimeType}]`];
}
