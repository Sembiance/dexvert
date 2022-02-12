import {Format} from "../../Format.js";

export class digitalFM extends Format
{
	name         = "Digital FM";
	ext          = [".dfm"];
	magic        = ["Digital-FM module", "DFM Song"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
