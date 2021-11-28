import {Format} from "../../Format.js";

export class dpx extends Format
{
	name         = "Digital Picture Exchange";
	website      = "http://fileformats.archiveteam.org/wiki/DPX";
	ext          = [".dpx"];
	mimeType     = "image/x-digital-picture-exchange";
	magic        = [/^Digital Moving Picture Exchange [Bb]itmap/, "DPX image data"];
	metaProvider = ["image"];
	converters   = ["convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
