import {Format} from "../../Format.js";

export class kodakDCR extends Format
{
	name         = "Kodak Pro Digital RAW";
	website      = "http://fileformats.archiveteam.org/wiki/Kodak";
	ext          = [".dcr"];
	magic        = [/^TIFF image data.*manufacturer=Kodak/];
	mimeType     = "image/x-kodak-dcr";
	metaProvider = ["darkTable"];
	converters   = ["darktable_cli", `abydosconvert[format:${this.mimeType}]`];
}
