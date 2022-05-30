import {Format} from "../../Format.js";

export class holyNoise extends Format
{
	name         = "The Holy Noise Module";
	ext          = [".thn"];
	magic        = [/^The Holy Noise [Mm]odule/];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
