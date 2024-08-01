import {Format} from "../../Format.js";

export class neoBookCartoon extends Format
{
	name           = "NeoBook Cartoon";
	ext            = [".car"];
	forbidExtMatch = true;
	magic          = ["NeoBook Cartoon"];
	converters     = ["foremost"];
}
