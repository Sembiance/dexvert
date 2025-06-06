import {Format} from "../../Format.js";

export class xcf extends Format
{
	name       = "The GIMP Image Format";
	website    = "http://fileformats.archiveteam.org/wiki/XCF";
	ext        = [".xcf"];
	mimeType   = "image/x-xcf";
	magic      = ["The GIMP image format", "GIMP image format", "GIMP XCF image data", "Gimp Image File Format", "image/x-xcf", "Gimp XCF image file :xcf:", /^fmt\/615( |$)/];
	converters = ["xcf2png", "gimp", "nconvert[format:xcf]"];
}
