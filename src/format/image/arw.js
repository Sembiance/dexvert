import {Format} from "../../Format.js";

export class arw extends Format
{
	name         = "Sony RAW";
	website      = "http://fileformats.archiveteam.org/wiki/Sony_ARW";
	ext          = [".arw"];
	magic        = ["Sony ARW RAW Image File", "Sony digital camera RAW image", /^fmt\/1127( |$)/];
	mimeType     = "image/x-sony-arw";
	metaProvider = ["image", "darkTable"];
	converters   = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
