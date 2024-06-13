import {Format} from "../../Format.js";

export class rekoCardset extends Format
{
	name       = "REKO Cardset";
	website    = "http://fileformats.archiveteam.org/wiki/REKO_Cardset";
	ext        = [".reko", ".deck", ".rkp"];
	magic      = [/^REKO .*cardset/, "Reko CardSet"];
	notes      = "Royo.RKP doesn't convert, not sure why. Neither does claudio_cards.reko, the width/height of the cards are different and rekotoppm doesn't handle it.";
	converters = ["reko2png"];
}
