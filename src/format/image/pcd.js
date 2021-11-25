import {Format} from "../../Format.js";

export class pcd extends Format
{
	name       = "Kodak Photo CD Picture";
	website    = "http://fileformats.archiveteam.org/wiki/Photo_CD";
	ext        = [".pcd"];
	mimeType   = "image/x-photo-cd";
	magic      = [/Kodak Photo CD [Ii]mage/, "Kodak PhotoCD bitmap"];
	converters = ["pcdtojpeg", "convert", `abydosconvert[format:${this.mimeType}]`, "nconvert"]
	metaProviders = ["image"];

	// If it fails, it often produces a 2x2 or 1x1 image, so exclude those
	verify = ({meta}) => meta.width>2 && meta.height>2;
}
