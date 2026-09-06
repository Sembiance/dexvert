import {Format} from "../../Format.js";

export class movingPuzzlesMV extends Format
{
	name           = "Moving Puzzles Video";
	ext            = [".mv"];
	forbidExtMatch = true;
	magic          = ["Moving Puzzles Video"];
	converters     = ["na_game_tool[format:mvpuz]", "vibe2avi"];
}
