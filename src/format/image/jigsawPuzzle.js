import {Format} from "../../Format.js";

export class jigsawPuzzle extends Format
{
	name       = "Jigsaw Puzzle";
	website    = "http://fileformats.archiveteam.org/wiki/Jigsaw_(Walter_A._Kuhn)";
	ext        = [".jig", ".sav"];
	magic      = ["Jigsaw Puzzle", "deark: jigsaw_wk"];
	converters = ["deark[module:jigsaw_wk]"];
}
