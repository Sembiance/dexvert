import {Format} from "../../Format.js";

export class raf extends Format
{
	name         = "Fujifilm RAW";
	website      = "http://fileformats.archiveteam.org/wiki/RAF";
	ext          = [".raf"];
	magic        = ["Fujifilm Raw image", /^fmt\/642( |$)/];
	mimeType     = "image/x-fuji-raf";
	metaProvider = ["image", "darkTable"];
	converters   = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
