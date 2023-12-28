import {Format} from "../../Format.js";

export class mrw extends Format
{
	name         = "Minolta RAW";
	website      = "http://fileformats.archiveteam.org/wiki/Minolta_MRW";
	ext          = [".mrw"];
	magic        = ["Minolta RAW", "Minolta Dimage camera raw", "Minolta Dimage RAW image", /^fmt\/669( |$)/];
	mimeType     = "image/x-minolta-mrw";
	metaProvider = ["image", "darkTable"];
	converters   = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
