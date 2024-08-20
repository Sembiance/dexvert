import {Format} from "../../Format.js";

export class abeEncoded extends Format
{
	name       = "ABE Encoded";
	website    = "http://fileformats.archiveteam.org/wiki/ABE";
	ext        = [".abe"];
	magic      = ["ABE encoded data"];
	converters = ["dabe"];
}
