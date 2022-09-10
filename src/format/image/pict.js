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
	converters     = [
		"deark", "recoil2png", "nconvert", "qtPicViewer", "soffice[outType:png]", "hiJaakExpress", "canvas", "picturePublisher",
		"deark[module:macbinary] -> deark",	// Can handle MacBinary-encoded PICT files such as samples 35, 039 and 06
		"imageAlchemy",
		"corelPhotoPaint",	// corelPhotoPaint sometimes just produces a 'QuickTime PICT' logo, not useful and not currently detected (see sample/image/pict/01)
		"tomsViewer",		// For some PICTS will only produce the 'thumbnail' (samples 35, 039 and 06). For these files, corelPhotoPaint produces a full image so this converter is tried after that one
		"convert"			// convert has a habit of just producing a black square
	];
}
