import {Format} from "../../Format.js";

export class picturePacker extends Format
{
	name       = "STOS Picture Packer";
	website    = "http://fileformats.archiveteam.org/wiki/Picture_Packer";
	ext        = [".pp3", ".pp2", ".pp1"];
	magic      = ["Picture Packer bitmap"];
	converters = ["deark", "konvertor"];
}
