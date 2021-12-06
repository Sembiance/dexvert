import {Format} from "../../Format.js";

export class deltaMusic extends Format
{
	name         = "Delta Music";
	ext          = [".dm2", ".dm"];
	magic        = ["Delta Music module", "Delta Music 2 module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:DeltaMusic1.3]", "uade123[player:DeltaMusic2.0]"];
}
