import {Format} from "../../Format.js";

export class macDraw extends Format
{
	name           = "MacDraw";
	website        = "http://fileformats.archiveteam.org/wiki/MacDraw";
	ext            = [".pict"];
	forbidExtMatch = true;
	magic          = ["MacDraw drawing"];
	metaProvider   = ["image"];
	converters     = ["deark", "nconvert", "convert"];
}
