import {Format} from "../../Format.js";

export class mng extends Format
{
	name         = "Multiple-image Network Graphics";
	website      = "http://fileformats.archiveteam.org/wiki/MNG";
	ext          = [".mng"];
	mimeType     = "video/x-mng";
	magic        = ["Multiple-image Network Graphics bitmap", "MNG video data", "video/x-mng", /^Multiple Network Graphics (\(Interlaced\) )?:mng:/, "deark: png (MNG)", /^fmt\/528( |$)/];
	metaProvider = ["image"];
	converters   = [`abydosconvert[format:${this.mimeType}][outType:webp]`, "convert[outType:webp]", `nconvert[extractAll][format:mng] -> *joinAsGIF[outType:gif]`];
}
