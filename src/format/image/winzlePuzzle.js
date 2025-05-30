import {Format} from "../../Format.js";

export class winzlePuzzle extends Format
{
	name       = "Winzle Puzzle";
	website    = "http://fileformats.archiveteam.org/wiki/Winzle_Puzzle";
	ext        = [".wzl"];
	magic      = ["Winzle puzzle", "deark: winzle"];
	weakMagic  = true;
	converters = ["deark[module:winzle]"];
}
