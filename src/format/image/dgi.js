import {Format} from "../../Format.js";

export class dgi extends Format
{
	name          = "Digi-Pic DGI";
	website       = "http://fileformats.archiveteam.org/wiki/DGI_(Digi-Pic)";
	ext           = [".dgi"];
	fileSize      = 64008;
	matchFileSize = true;
	converters    = ["deark[module:dgi]", "dgiwind"];
}
