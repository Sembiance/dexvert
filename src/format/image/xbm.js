import {Format} from "../../Format.js";

const _XBM_MAGIC = ["X Bitmap", "xbm image", "piped xbm sequence (xbm_pipe)", "X BitMap :xbm:", /^x-fmt\/(207|299)( |$)/];
export {_XBM_MAGIC};

export class xbm extends Format
{
	name         = "X11 Bitmap";
	website      = "http://fileformats.archiveteam.org/wiki/XBM";
	ext          = [".xbm", ".bm"];
	magic        = _XBM_MAGIC;
	idMeta       = ({macFileType}) => macFileType==="XBM ";
	mimeType     = "image/x-xbitmap";
	metaProvider = ["image"];
	converters   = [
		"wuimg[format:c]",	// only one that handles 3270.icon and iv.X correctly
		"convert", "gimp", "nconvert[format:xbm][matchType:magic]", "imconv[format:xbm][matchType:magic]", "tkimgConvert[matchType:magic]"
		//"hiJaakExpress[matchType:magic]", "canvas[matchType:magic]", "tomsViewer[matchType:magic]"
	];
}
