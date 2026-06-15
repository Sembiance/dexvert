import {Format} from "../../Format.js";

export class movingPuzzlesMV extends Format
{
	name           = "Moving Puzzles Video";
	ext            = [".mv"];
	forbidExtMatch = true;
	magic          = ["Moving Puzzles Video"];
	converters     = ["vibe2avi"];
}
