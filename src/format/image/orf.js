import {Format} from "../../Format.js";

export class orf extends Format
{
	name         = "Olympus RAW";
	website      = "http://fileformats.archiveteam.org/wiki/Olympus_ORF";
	ext          = [".orf"];
	magic        = ["Olympus RAW", "Olympus ORF raw image data", "Olympus digital camera RAW image", "image/x-olympus-orf", "deark: tiff (Olympus RAW)", /^fmt\/668( |$)/];
	mimeType     = "image/x-olympus-orf";
	metaProvider = ["image", "darkTable"];
	converters   = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
