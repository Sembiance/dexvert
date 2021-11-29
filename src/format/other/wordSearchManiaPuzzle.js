import {Format} from "../../Format.js";

export class wordSearchManiaPuzzle extends Format
{
	name           = "Wordsearch Mania! Puzzle";
	ext            = [".wsp"];
	forbidExtMatch = true;
	magic          = ["Wordsearch Mania! Puzzle"];
	converters     = ["strings"];
}
