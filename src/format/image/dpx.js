import {Format} from "../../Format.js";

export class dpx extends Format
{
	name         = "Digital Picture Exchange";
	website      = "http://fileformats.archiveteam.org/wiki/DPX";
	ext          = [".dpx"];
	mimeType     = "image/x-digital-picture-exchange";
	magic        = [/^Digital Moving Picture Exchange [Bb]itmap/, "DPX image data", /^fmt\/(193|541)( |$)/];
	metaProvider = ["image"];
	converters   = ["convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];	// iconvert also supports it but produces bad output
}
