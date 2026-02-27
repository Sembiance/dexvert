import {Format} from "../../Format.js";

export class witcher2Archive extends Format
{
	name           = "Witcher 2 Archive";
	ext            = [".dzip"];
	forbidExtMatch = true;
	magic          = ["The Witcher 2 game data archive", "dragon: DZIP "];
	converters     = ["dragonUnpacker[types:DZIP]"];
}
