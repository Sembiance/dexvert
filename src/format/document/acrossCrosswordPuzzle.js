import {Format} from "../../Format.js";

export class acrossCrosswordPuzzle extends Format
{
	name           = "Across Crossword Puzzle";
	ext            = [".puz"];
	forbidExtMatch = true;
	magic          = ["PUZ crossword puzzle", "Across crossword puzzle"];
	converters     = ["strings"];
}
