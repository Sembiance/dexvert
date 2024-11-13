import {Format} from "../../Format.js";

export class abcNotation extends Format
{
	name       = "ABC Musical Notation";
	website    = "http://fileformats.archiveteam.org/wiki/ABC_(musical_notation)";
	ext        = [".abc", ".abh"];
	magic      = ["ABC notation", "text/vnd.abc"];
	weakMagic  = true;
	converters = ["abc2mid"];
}
