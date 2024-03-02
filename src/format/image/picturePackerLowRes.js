import {Format} from "../../Format.js";

export class picturePackerLowRes extends Format
{
	name       = "STOS Picture Packer (Low-Res)";
	website    = "http://fileformats.archiveteam.org/wiki/Picture_Packer";
	ext        = [".pp1"];
	mimeType   = "image/x-stos-picturepacker-lowres";
	magic      = ["Picture Packer bitmap"];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
