import {Format} from "../../Format.js";

export class youDontKnowJack extends Format
{
	name           = "You Don't Know Jack Archive";
	ext            = [".srf"];
	forbidExtMatch = true;
	magic          = ["You Don't Know Jack game data archive"];
	converters     = ["gameextractor"];
}
