import {Format} from "../../Format.js";

export class crusadeFPKVideo extends Format
{
	name           = "Crusade FPK Video";
	ext            = [".fpk"];
	forbidExtMatch = true;
	magic          = ["Crusade FPK Video"];
	converters     = ["na_game_tool[format:fpk]"];
}
