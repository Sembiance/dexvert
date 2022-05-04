import {Format} from "../../Format.js";

export class macDraw extends Format
{
	name           = "MacDraw";
	website        = "http://fileformats.archiveteam.org/wiki/MacDraw";
	ext            = [".pict"];
	forbidExtMatch = true;
	magic          = ["MacDraw drawing", /^fmt\/1427( |$)/];
	metaProvider   = ["image"];
	converters     = ["deark", "nconvert", "soffice[outType:png]", "convert"];	// convert has a habit of producing just a black square
}
