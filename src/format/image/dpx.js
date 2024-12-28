import {Format} from "../../Format.js";

export class dpx extends Format
{
	name         = "Digital Picture Exchange";
	website      = "http://fileformats.archiveteam.org/wiki/DPX";
	ext          = [".dpx"];
	mimeType     = "image/x-digital-picture-exchange";
	magic        = [/^Digital Moving Picture Exchange [Bb]itmap/, "DPX image data", "image/dpx", "piped dpx sequence (dpx_pipe)", /^fmt\/(193|541)( |$)/];
	metaProvider = ["image"];
	converters   = ["convert", "ffmpeg[format:dpx_pipe][outType:png]", "wuimg", "nconvert"];	// iconvert also supports it but produces bad output
}
