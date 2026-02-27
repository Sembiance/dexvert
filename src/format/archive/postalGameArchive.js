import {Format} from "../../Format.js";

export class postalGameArchive extends Format
{
	name           = "Postal game Archive";
	ext            = [".sak"];
	forbidExtMatch = true;
	magic          = ["Postal game data Archive", /^geArchive: SAK_SAK( |$)/, "dragon: SAK "];
	converters     = ["gameextractor[codes:SAK_SAK]", "dragonUnpacker[types:SAK]"];
}
