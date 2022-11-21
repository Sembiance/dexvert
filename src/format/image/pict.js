import {Format} from "../../Format.js";

export class pict extends Format
{
	name           = "Macintosh Picture Format";
	website        = "http://fileformats.archiveteam.org/wiki/PICT";
	ext            = [".pict", ".pic", ".pct"];
	forbidExtMatch = true;	// way too common
	mimeType       = "image/pict";
	magic          = ["QuickDraw/PICT bitmap", "Macintosh PICT", "Claris clip art", /^fmt\/341( |$)/, /^x-fmt\/80( |$)/];
	metaProvider   = ["image"];
	converters     = [
		"deark[mac][recombine]", "recoil2png", "qtPicViewer", "soffice[outType:png]",
		"canvas",			// canvas seems to properly recombine sub-bitmaps into a final image (sample/image/pict/Daniel  and  2kangaro  and  bbq)
		"hiJaakExpress", "picturePublisher",
		"deark[module:macbinary] -> deark",	// Can handle MacBinary-encoded PICT files such as samples 35, 039 and 06
		"imageAlchemy",		// while this properly recombines sub-bitmaps, it's DOS based and so we don't trust it very much
		"corelDRAW",
		"corelPhotoPaint",	// corelPhotoPaint sometimes just produces a 'QuickTime PICT' logo, not useful and not currently detected (see sample/image/pict/01)
		"tomsViewer",		// For some PICTS will only produce the 'thumbnail' (samples 35, 039 and 06). For these files, corelPhotoPaint produces a full image so this converter is tried after that one
		"nconvert",			// nconvert produces just a black image PICT v2 format picts: p#.pic
		"convert"			// convert has a habit of just producing a black square
	];
}
