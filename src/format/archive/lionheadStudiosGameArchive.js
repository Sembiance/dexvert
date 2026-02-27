import {Format} from "../../Format.js";

export class lionheadStudiosGameArchive extends Format
{
	name           = "Lionhead Studios game archive";
	ext            = [".sad"];
	forbidExtMatch = true;
	magic          = ["Generic Lionhead Studios game data", /^geArchive: SAD_LIONHEAD( |$)/, "dragon: LHAB "];
	converters     = ["gameextractor[codes:SAD_LIONHEAD]", "dragonUnpacker[types:LHAB]"];
}
