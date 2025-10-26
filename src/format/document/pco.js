import {Format} from "../../Format.js";

export class pco extends Format
{
	name       = "PC-Outline Document";
	website    = "http://fileformats.archiveteam.org/wiki/PC-Outline";
	ext        = [".pco"];
	magic      = ["PC-Outline / Brown Bag Outline outline"];
	converters = ["pco"];
}
