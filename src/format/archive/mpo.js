import {Format} from "../../Format.js";

export class mpo extends Format
{
	name       = "Multi-Picture Format";
	website    = "http://fileformats.archiveteam.org/wiki/Multi-Picture_Format";
	ext        = [".mpo"];
	magic      = ["JPEG image data", "deark: jpeg (JPEG/MPO)", "MPO :mpo:"];
	weakMagic  = true;
	mimeType   = "image/x-mpo";
	converters = ["nconvert[format:mpo][extractAll]", "deark[module:jpeg]", "noesis[type:image]"];
}
