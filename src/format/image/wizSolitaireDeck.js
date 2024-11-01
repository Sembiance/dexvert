import {Format} from "../../Format.js";

export class wizSolitaireDeck extends Format
{
	name       = "Wiz Solitaire Deck";
	website    = "http://fileformats.archiveteam.org/wiki/Wiz_Solitaire";
	ext        = [".deck"];
	magic      = ["Wiz Solitaire Deck", "Wiz Solitaire cards Deck"];
	converters = ["deark[module:wizsolitaire]"];
}
