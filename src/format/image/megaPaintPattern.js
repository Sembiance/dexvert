import {Format} from "../../Format.js";

export class megaPaintPattern extends Format
{
	name           = "MegaPaint Pattern";
	website        = "http://fileformats.archiveteam.org/wiki/MegaPaint_BLD";
	ext            = [".pat"];
	forbidExtMatch = true;
	magic          = ["MegaPaint Pattern"];
	converters     = ["deark"];
}
