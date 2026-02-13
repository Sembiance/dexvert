import {Format} from "../../Format.js";

export class wirelessBMP extends Format
{
	name         = "Wireless Bitmap";
	website      = "http://fileformats.archiveteam.org/wiki/WBMP";
	ext          = [".wbmp", ".wap", ".wbm"];
	magic        = ["WAP bmp :wbmp:"];
	mimeType     = "image/vnd.wap.wbmp";
	metaProvider = ["image"];
	converters   = ["convert", "wuimg[format:wbmp]", "nconvert[format:wbmp]", "powerpaint[format:wbmp]"];	// "canvas", "tomsViewer"
}
