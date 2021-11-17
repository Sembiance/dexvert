import {Format} from "../../Format.js";

export class pcx extends Format
{
	name          = "PC Paintbrush Image";
	website       = "http://fileformats.archiveteam.org/wiki/PCX";
	ext           = [".pcx"];
	mimeType      = "image/x-pcx";
	magic         = ["PCX bitmap", /^PCX ver.* image data/, /^PCX$/];
	converters    = ["graphicWorkshopProfessional"]; // TODO: ["nconvert", "convert", "deark", "imageAlchemy", "graphicWorkshopProfessional"];
	metaProviders = ["image"];
}
