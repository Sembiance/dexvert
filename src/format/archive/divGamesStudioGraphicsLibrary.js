import {Format} from "../../Format.js";

export class divGamesStudioGraphicsLibrary extends Format
{
	name       = "DIV GamesStudio Graphics Library";
	website    = "http://fileformats.archiveteam.org/wiki/DIV_Games_Studio";
	ext        = [".fpg"];
	magic      = ["DIV Games Studio Graphics Library", "deark: div_fpg (DIV ", "DIV Game Studio Multi-Map :fpg:", "Fenix Multi-Map :fpg:"];
	converters = ["deark[module:div_fpg]", "nconvert[format:fpg][extractAll]"];
}
