import {Format} from "../../Format.js";

export class rekoCardset extends Format
{
	name       = "REKO Cardset";
	website    = "https://www.rekonet.org/index.html";
	ext        = [".reko", ".deck", ".rkp"];
	magic      = ["REKO cardset", "Reko CardSet"];
	notes      = "Royo.RKP doesn't convert, not sure why";
	converters = ["reko2png"];
}
