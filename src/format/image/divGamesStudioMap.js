import {Format} from "../../Format.js";

export class divGamesStudioMap extends Format
{
	name           = "DIV GamesStudio Map";
	website        = "http://fileformats.archiveteam.org/wiki/DIV_Games_Studio";
	ext            = [".map"];
	forbidExtMatch = true;
	magic          = ["DIV Games Studio Map", "deark: div_map (DIV MAP)", "DIV Game Studio Map :map:"];
	converters     = ["deark[module:div_map]", "nconvert[format:map]"];
}
