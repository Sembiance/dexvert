import {Format} from "../../Format.js";

export class jpegXL extends Format
{
	name       = "JPEG XL";
	website    = "http://fileformats.archiveteam.org/wiki/JPEG_XL";
	ext        = [".jxl"];
	mimeType   = "image/jxl";
	magic      = ["JPEG XL codestream", "JPEG XL bitmap", "JPEG XL container", /^fmt\/(1484|1485)( |$)/];
	converters = ["gimp"];	// ["djxl", `abydosconvert[format:${this.mimeType}]`];
}
