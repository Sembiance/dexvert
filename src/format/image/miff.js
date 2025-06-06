import {Format} from "../../Format.js";

export class miff extends Format
{
	name         = "Magick Image File Format";
	website      = "http://fileformats.archiveteam.org/wiki/MIFF";
	ext          = [".miff", ".mif"];
	mimeType     = "image/x-miff";
	magic        = ["MIFF image data", "ImageMagick Machine independent File Format bitmap", /^Image Magick.* :miff:$/, /^fmt\/930( |$)/];
	metaProvider = ["image"];
	converters   = ["imconv[format:miff]", "convert", "nconvert[format:miff]"];
}
