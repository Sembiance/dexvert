import {Format} from "../../Format.js";

export class pcx extends Format
{
	name         = "PC Paintbrush Image";
	website      = "http://fileformats.archiveteam.org/wiki/PCX";
	ext          = [".pcx", ".pcc"];
	mimeType     = "image/x-pcx";
	magic        = ["PCX bitmap", /^PCX ver.* image data/, /^PCX$/, /^fmt\/90( |$)/];
	metaProvider = ["image"];
	converters   = ["nconvert", "convert", "deark", "gimp", "imageAlchemy", "graphicWorkshopProfessional", "hiJaakExpress", "picturePublisher", "corelPhotoPaint", "canvas", "tomsViewer"];
}
