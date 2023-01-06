import {Format} from "../../Format.js";

export class divGamesStudioGraphicsLibrary extends Format
{
	name       = "DIV GamesStudio Graphcis Library";
	ext        = [".fpg"];
	magic      = ["DIV Games Studio Graphics Library"];
	converters = ["nconvert[extractAll]"];
}
