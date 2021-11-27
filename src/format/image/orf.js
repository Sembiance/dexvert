import {Format} from "../../Format.js";

export class orf extends Format
{
	name          = "Olympus RAW";
	website       = "http://fileformats.archiveteam.org/wiki/ORF";
	ext           = [".orf"];
	magic         = ["Olympus RAW", "Olympus ORF raw image data", "Olympus digital camera RAW image"];
	mimeType      = "image/x-olympus-orf";
	converters    = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"]
	metaProviders = ["image", "darkTable"];
}
