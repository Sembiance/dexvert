import {Format} from "../../Format.js";

export class xbm extends Format
{
	name         = "X11 Bitmap";
	website      = "http://fileformats.archiveteam.org/wiki/XBM";
	ext          = [".xbm", ".bm"];
	magic        = ["X Bitmap", "xbm image", "piped xbm sequence (xbm_pipe)", /^x-fmt\/207( |$)/];
	idMeta       = ({macFileType}) => macFileType==="XBM ";
	mimeType     = "image/x-xbitmap";
	metaProvider = ["image"];
	converters   = [
		"convert", "gimp", "imconv[format:xbm][matchType:magic]", "wuimg",
		"hiJaakExpress[matchType:magic]", "canvas[matchType:magic]", "tomsViewer[matchType:magic]"
	];
}
