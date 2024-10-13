import {Format} from "../../Format.js";

export class pentaxRaw extends Format
{
	name         = "Pentax RAW";
	website      = "http://fileformats.archiveteam.org/wiki/Pentax_PEF";
	ext          = [".pef", ".ptx"];
	magic        = ["Pentax RAW image", /^fmt\/1781( |$)/];
	mimeType     = "image/x-pentax-pef";
	metaProvider = ["image", "darkTable"];
	converters   = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert[matchType:magic]"];
}
