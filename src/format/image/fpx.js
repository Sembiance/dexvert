import {Format} from "../../Format.js";

export class fpx extends Format
{
	name         = "Kodak FlashPix";
	website      = "http://fileformats.archiveteam.org/wiki/FPX";
	ext          = [".fpx"];
	mimeType     = "image/vnd.fpx";
	magic        = ["Generic OLE2", "Composite Document File", "OLE2 Compound Document Format"];
	metaProvider = ["image"];
	converters   = ["convert", "corelPhotoPaint"];	// canvas also supports this format, but only in a non-raster way which I don't trust enough with this generatic magic/ext
}
