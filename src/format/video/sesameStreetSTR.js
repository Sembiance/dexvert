import {Format} from "../../Format.js";

export class sesameStreetSTR extends Format
{
	name           = "Sesame Street STR Video";
	ext            = [".str"];
	forbidExtMatch = true;
	magic          = ["Sesame Street STR Video"];
	converters     = ["na_game_tool[format:ssstr]"];
}
