import {Format} from "../../Format.js";

export class ppm extends Format
{
	name         = "Portable Pixmap";
	website      = "http://fileformats.archiveteam.org/wiki/Netpbm_formats";
	ext          = [".ppm", ".pnm"];
	mimeType     = "image/x-portable-pixmap";
	magic        = ["Portable PixMap bitmap", "Portable Pixel Map", /^Netpbm image data .*pixmap$/];
	metaProvider = ["image"];
	converters   = ["convert", "hiJaakExpress"];
}

