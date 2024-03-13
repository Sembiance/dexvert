import {Format} from "../../Format.js";

export class raf extends Format
{
	name         = "Fujifilm RAW";
	website      = "http://fileformats.archiveteam.org/wiki/Fujifilm_RAF";
	ext          = [".raf"];
	magic        = ["Fujifilm Raw image", "Fujifilm RAF raw image data", /^fmt\/642( |$)/];
	mimeType     = "image/x-fuji-raf";
	metaProvider = ["image", "darkTable"];
	converters   = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
