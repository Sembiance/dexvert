import {Format} from "../../Format.js";

export class txs extends Format
{
	name       = "TXS";
	website    = "http://fileformats.archiveteam.org/wiki/TXS";
	ext        = [".txs"];
	converters = ["recoil2png"];
}
