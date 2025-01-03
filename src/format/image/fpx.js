import {Format} from "../../Format.js";

export class fpx extends Format
{
	name         = "Kodak FlashPix";
	website      = "http://fileformats.archiveteam.org/wiki/FlashPix";
	ext          = [".fpx"];
	mimeType     = "image/vnd.fpx";
	magic        = ["Kodak FlashPix bitmap", /^OLE 2 Compound Document.*FlashPIX/, /^x-fmt\/56( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="FPix" && macFileCreator==="LPSH";
	metaProvider = ["image"];
	converters   = ["convert", "photoDraw", "corelPhotoPaint"];	// canvas also supports this format, but only in a non-raster way which I don't trust enough with this generatic magic/ext
}
