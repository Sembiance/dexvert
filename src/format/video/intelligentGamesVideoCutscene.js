import {Format} from "../../Format.js";

export class intelligentGamesVideoCutscene extends Format
{
	name           = "Intelligent Games Video/cutscene";
	website        = "https://wiki.multimedia.cx/index.php/Intelligent_Games_MOV";
	ext            = [".mov"];
	forbidExtMatch = true;
	magic          = ["Intelligent Games Video/cutscene"];
	weakMagic      = true;
	converters     = ["na_game_tool[format:azmov]"];
}
