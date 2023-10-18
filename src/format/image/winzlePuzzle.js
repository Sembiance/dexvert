import {Format} from "../../Format.js";

export class winzlePuzzle extends Format
{
	name       = "Winzle Puzzle";
	website    = "http://fileformats.archiveteam.org/wiki/Winzle_Puzzle";
	ext        = [".wzl"];
	magic      = ["Winzle puzzle"];
	converters = ["deark[module:winzle]"];
}
