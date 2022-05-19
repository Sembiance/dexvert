import {Format} from "../../Format.js";

export class pict extends Format
{
	name           = "Macintosh Picture Format";
	website        = "http://fileformats.archiveteam.org/wiki/PICT";
	ext            = [".pict", ".pic", ".pct"];
	forbidExtMatch = true;	// way too common
	mimeType       = "image/pict";
	magic          = ["QuickDraw/PICT bitmap", "Macintosh PICT Image", "Claris clip art", /^fmt\/341( |$)/, /^x-fmt\/80( |$)/];
	metaProvider   = ["image"];
	converters     = ["deark", "recoil2png", "nconvert", "qtPicViewer", "soffice[outType:png]", "hiJaakExpress", "corelPhotoPaint", "canvas", "picturePublisher", "convert"];	// convert has a habit of producing just a black square
}
