import {Format} from "../../Format.js";

export class jigsawPuzzle extends Format
{
	name       = "Jigsaw Puzzle";
	website    = "http://fileformats.archiveteam.org/wiki/Jigsaw_(Walter_A._Kuhn)";
	ext        = [".jig", ".sav"];
	magic      = ["Jigsaw Puzzle", "deark: jigsaw_wk", "JIGSAW :jig:"];
	converters = ["deark[module:jigsaw_wk]"];	// nconvert doesn't handle color and messes some other stuff up
}
