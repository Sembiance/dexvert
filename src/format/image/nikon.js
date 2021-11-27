import {Format} from "../../Format.js";

export class nikon extends Format
{
	name          = "Nikon Electronic Format";
	website       = "http://fileformats.archiveteam.org/wiki/Nikon";
	ext           = [".nef", ".nrw"];
	magic         = ["Nikon raw image", /^TIFF image data.*manufacturer=NIKON/];
	mimeType      = "image/x-nikon-nef";
	converters    = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"]
	metaProviders = ["image", "darkTable"];
}
