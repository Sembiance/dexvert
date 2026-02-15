import {Format} from "../../Format.js";

export class msxInterchangeFormat extends Format
{
	name       = "MSX Interchange Format";
	website    = "http://fileformats.archiveteam.org/wiki/MIF_(MSX)";
	ext        = [".mif"];
	converters = ["recoil2png[format:MIF]"];
}
