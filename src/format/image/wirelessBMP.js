import {Format} from "../../Format.js";

export class wirelessBMP extends Format
{
	name         = "Wireless Bitmap";
	website      = "http://fileformats.archiveteam.org/wiki/WBMP";
	ext          = [".wbmp", ".wap", "wbm"];
	mimeType     = "image/vnd.wap.wbmp";
	metaProvider = ["image"];
	converters   = ["convert", "canvas", "tomsViewer"];
}
