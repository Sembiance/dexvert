import {Format} from "../../Format.js";

export class worldFairyTalesIBMVideo extends Format
{
	name           = "World Fair Tables IBM Video";
	ext            = [".tj", ".tj_"];
	forbidExtMatch = true;
	magic          = ["World Fair Tales IBM WEAK"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:ibm]"];
}
