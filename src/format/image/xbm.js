import {Format} from "../../Format.js";

export class xbm extends Format
{
	name         = "X11 Bitmap";
	website      = "http://fileformats.archiveteam.org/wiki/XBM";
	ext          = [".xbm", ".bm"];
	magic        = ["X Bitmap", "xbm image", /^x-fmt\/207( |$)/];
	idMeta       = ({macFileType}) => macFileType==="XBM ";
	mimeType     = "image/x-xbitmap";
	metaProvider = ["image"];
	converters   = ["convert", "gimp", "hiJaakExpress", "canvas", "tomsViewer"];
}
