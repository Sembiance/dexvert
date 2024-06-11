import {Format} from "../../Format.js";

export class picturePackerMedRes extends Format
{
	name       = "STOS Picture Packer (Med-Res)";
	website    = "http://fileformats.archiveteam.org/wiki/Picture_Packer";
	ext        = [".pp2"];
	mimeType   = "image/x-stos-picturepacker-medres";
	magic      = ["Picture Packer bitmap"];
	converters = ["deark", `abydosconvert[format:${this.mimeType}]`, "konvertor"];
}
