import {Format} from "../../Format.js";

export class erf extends Format
{
	name         = "Epson RAW File";
	website      = "http://fileformats.archiveteam.org/wiki/Epson_ERF";
	ext          = [".erf"];
	magic        = ["Epson Raw Image Format", /^TIFF image data.*description=EPSON DSC/, /^fmt\/641( |$)/];
	mimeType     = "image/x-epson-erf";
	metaProvider = ["image", "darkTable"];
	converters   = ["darktable_cli", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
