import {Format} from "../../Format.js";

export class pcx extends Format
{
	name          = "PC Paintbrush Image";
	website       = "http://fileformats.archiveteam.org/wiki/PCX";
	ext           = [".pcx"];
	mimeType      = "image/x-pcx";
	magic         = ["PCX bitmap", /^PCX ver.* image data/, /^PCX$/];
	converters    = ["word97 -> dexvert[asFormat:document/wordDoc][deleteInput] -> programid[flag1:flag1Value][flag2][flag3:flag3Value]", "nconvert", "convert", "deark", "imageAlchemy", "graphicWorkshopProfessional"];
	metaProviders = ["image"];
}
