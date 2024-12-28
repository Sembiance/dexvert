import {Format} from "../../Format.js";

export class jpegXL extends Format
{
	name       = "JPEG XL";
	website    = "http://fileformats.archiveteam.org/wiki/JPEG_XL";
	ext        = [".jxl"];
	mimeType   = "image/jxl";
	magic      = ["JPEG XL codestream", "JPEG XL bitmap", "JPEG XL container", "image/jxl", "piped jpegxl sequence (jpegxl_pipe)", "Animated JPEG XL (jpegxl_anim)", /^fmt\/(1484|1485)( |$)/];
	converters = ["iconvert", "gimp", "wuimg"];	// ["djxl", `abydosconvert[format:${this.mimeType}]`];
}
