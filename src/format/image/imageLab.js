import {Format} from "../../Format.js";

export class imageLab extends Format
{
	name       = "ImageLab Image";
	website    = "http://fileformats.archiveteam.org/wiki/ImageLab/PrintTechnic";
	ext        = [".b_w", ".b&w"];
	mimeType   = "image/x-imagelab";
	magic      = ["ImageLab bitmap", "ImageLab :ilab:"];
	converters = [
		"nconvert[format:ilab]",
		"recoil2png"	// can't pass apresend as flag, so leave out format
		//`abydosconvert[format:${this.mimeType}]`
	];
}
