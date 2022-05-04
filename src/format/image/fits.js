import {Format} from "../../Format.js";

export class fits extends Format
{
	name       = "Flexible Image Transport System";
	website    = "http://fileformats.archiveteam.org/wiki/Flexible_Image_Transport_System";
	ext        = [".fit", ".fits", ".fts", ".fz"];
	mimeType   = "image/fits";
	magic      = ["Flexible Image Transport System", "FITS image data", /^x-fmt\/383( |$)/];
	converters = ["nconvert", `abydosconvert[format:${this.mimeType}]`, "gimp"];
}
