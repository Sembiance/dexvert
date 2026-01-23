import {Format} from "../../Format.js";

export class microidsGRN extends Format
{
	name           = "Microids GRN Video";
	ext            = [".grn"];
	forbidExtMatch = true;
	magic          = ["Microids GRN Video"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:grn]"];
}
