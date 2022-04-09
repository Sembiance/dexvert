import {Format} from "../../Format.js";

export class janesLongbow2 extends Format
{
	name           = "Jane's Longbow 2 Archive";
	ext            = [".tre"];
	forbidExtMatch = true;
	magic          = ["Jane's Longbow 2 game data archive"];
	converters     = ["gameextractor"];
}
