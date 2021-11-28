import {Format} from "../../Format.js";

export class pict extends Format
{
	name           = "Macintosh Picture Format";
	website        = "http://fileformats.archiveteam.org/wiki/PICT";
	ext            = [".pict", ".pic", ".pct"];
	forbidExtMatch = true;
	mimeType       = "image/pict";
	magic          = ["QuickDraw/PICT bitmap", "Macintosh PICT Image", "Claris clip art"];
	metaProvider   = ["image"];
	converters     = ["deark", "recoil2png", "nconvert", "convert", "qtPicViewer", "soffice[outType:png]"];
}
