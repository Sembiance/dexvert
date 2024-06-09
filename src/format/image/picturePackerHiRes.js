import {Format} from "../../Format.js";

export class picturePackerHiRes extends Format
{
	name       = "STOS Picture Packer (Hi-Res)";
	website    = "http://fileformats.archiveteam.org/wiki/Picture_Packer";
	ext        = [".pp3"];
	mimeType   = "image/x-stos-picturepacker-hires";
	magic      = ["Picture Packer bitmap"];
	converters = ["deark[module:stos_pp3]", `abydosconvert[format:${this.mimeType}]`, "konvertor"];
}
