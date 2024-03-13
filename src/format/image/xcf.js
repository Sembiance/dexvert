import {Format} from "../../Format.js";

export class xcf extends Format
{
	name       = "The GIMP Image Format";
	website    = "http://fileformats.archiveteam.org/wiki/XCF";
	ext        = [".xcf"];
	mimeType   = "image/x-xcf";
	magic      = ["The GIMP image format", "GIMP image format", "GIMP XCF image data", "Gimp Image File Format", /^fmt\/615( |$)/];
	converters = ["xcf2png", "gimp"];
}
