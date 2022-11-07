import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class macPaint extends Format
{
	name           = "MacPaint Image";
	website        = "http://fileformats.archiveteam.org/wiki/MacPaint";
	ext            = [".mac", ".pntg", ".pic", ".macp"];
	magic          = ["MacPaint image data", "Mac MacPaint bitmap (MacBinary)", /^fmt\/(161|1429)( |$)/, /^x-fmt\/161( |$)/];
	mimeType       = "image/x-macpaint";
	forbiddenMagic = ["Installer VISE Mac package", ...TEXT_MAGIC];
	metaProvider   = ["image"];
	converters     = ["deark[mac]", `abydosconvert[format:${this.mimeType}]`, "convert", "hiJaakExpress", "pv[matchType:magic]", "corelPhotoPaint", "tomsViewer"];
}
