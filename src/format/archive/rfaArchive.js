import {Format} from "../../Format.js";

export class rfaArchive extends Format
{
	name           = "RFA Archive";
	ext            = [".rfa"];
	forbidExtMatch = true;
	magic          = [/^geArchive: RFA_REFRACTOR2( |$)/, "dragon: RFA "];
	converters     = ["gameextractor[codes:RFA_REFRACTOR2]", "dragonUnpacker[types:RFA]"];
}
