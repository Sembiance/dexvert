import {Format} from "../../Format.js";

export class pbm extends Format
{
	name         = "Portable Bitmap";
	website      = "http://fileformats.archiveteam.org/wiki/PBM";
	ext          = [".pbm", ".pnm"];
	mimeType     = "image/x-portable-bitmap";
	magic        = ["Portable BitMap", "Portable Bitmap Image", /^Netpbm image data .*bitmap$/];
	metaProvider = ["image"];
	converters   = ["convert", "gimp", "hiJaakExpress", "canvas"];
}
