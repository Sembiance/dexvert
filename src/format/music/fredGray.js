import {Format} from "../../Format.js";

export class fredGray extends Format
{
	name         = "Fred Gray Module";
	ext          = [".gray"];
	magic        = ["Fred Gray module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:FredGray]"];
}
