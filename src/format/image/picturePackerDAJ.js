import {Format} from "../../Format.js";

export class picturePackerDAJ extends Format
{
	name       = "STOS Picture Packer (DAJ Variant)";
	website    = "http://fileformats.archiveteam.org/wiki/Picture_Packer";
	ext        = [".daj"];
	magic      = ["Picture Packer bitmap", "deark: stos_daj (STOS Packed Screen / Picture Packer)"];
	weakMagic  = true;
	converters = ["deark[module:stos_daj]", "konvertor"];
}
