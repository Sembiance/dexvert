import {Format} from "../../Format.js";

export class nikon extends Format
{
	name         = "Nikon Electronic Format";
	website      = "http://fileformats.archiveteam.org/wiki/Nikon";
	ext          = [".nef", ".nrw"];
	magic        = ["Nikon raw image", /^fmt\/202( |$)/];	// Used to use this, but it's too loose (sample/image/jpg/orange_zip.jpg): /^TIFF image data.*manufacturer=NIKON/
	mimeType     = "image/x-nikon-nef";
	metaProvider = ["image", "darkTable"];
	converters   = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`];
}
