import {Format} from "../../Format.js";

export class xbm extends Format
{
	name         = "X11 Bitmap";
	website      = "http://fileformats.archiveteam.org/wiki/XBM";
	ext          = [".xbm", ".bm"];
	magic        = [/^x-fmt\/207( |$)/];
	mimeType     = "image/x-xbitmap";
	metaProvider = ["image"];
	converters   = ["convert", "gimp", "hiJaakExpress", "canvas", "tomsViewer"];
}
