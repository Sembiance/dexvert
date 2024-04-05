import {Format} from "../../Format.js";

export class pcx extends Format
{
	name         = "PC Paintbrush Image";
	website      = "http://fileformats.archiveteam.org/wiki/PCX";
	ext          = [".pcx", ".pcc"];
	mimeType     = "image/x-pcx";
	magic        = ["PCX bitmap", /^PCX ver.* image data/, /^PCX$/, /^fmt\/(87|88|90)( |$)/];
	metaProvider = ["image"];
	converters   = [
		"nconvert", "convert", "deark[module:pcx]", "iio2png", "gimp",
		...["imageAlchemy", "graphicWorkshopProfessional", "photoDraw", "hiJaakExpress", "picturePublisher", "corelPhotoPaint", "canvas5", "canvas", "tomsViewer", "corelDRAW", "keyViewPro"].map(v => `${v}[strongMatch]`)
	];
}
