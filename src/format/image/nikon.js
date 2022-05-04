import {Format} from "../../Format.js";

export class nikon extends Format
{
	name         = "Nikon Electronic Format";
	website      = "http://fileformats.archiveteam.org/wiki/Nikon";
	ext          = [".nef", ".nrw"];
	magic        = ["Nikon raw image", /^TIFF image data.*manufacturer=NIKON/, /^fmt\/202( |$)/];
	mimeType     = "image/x-nikon-nef";
	metaProvider = ["image", "darkTable"];
	converters   = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
