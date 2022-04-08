import {Format} from "../../Format.js";

export class pcx extends Format
{
	name         = "PC Paintbrush Image";
	website      = "http://fileformats.archiveteam.org/wiki/PCX";
	ext          = [".pcx"];
	mimeType     = "image/x-pcx";
	magic        = ["PCX bitmap", /^PCX ver.* image data/, /^PCX$/];
	metaProvider = ["image"];
	converters   = ["nconvert", "convert", "deark", "imageAlchemy", "graphicWorkshopProfessional", "hiJaakExpress", "corelPhotoPaint"];
}
