import {Format} from "../../Format.js";

export class dgi extends Format
{
	name          = "Digi-Pic DGI";
	website       = "http://fileformats.archiveteam.org/wiki/DGI_(Digi-Pic)";
	ext           = [".dgi"];
	fileSize      = 64008;
	magic         = ["Digi-Pic 2"];
	converters    = ["deark[module:dgi][matchType:magic]", "dgiwind"];
}
