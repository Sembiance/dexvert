import {Format} from "../../Format.js";

export class lemmingsRevolutionGameArchive extends Format
{
	name           = "Lemmings Revolution game archive";
	ext            = [".box"];
	forbidExtMatch = true;
	magic          = ["Lemmings Revolution game data archive", /^geArchive: BOX_LEMBOX( |$)/, "dragon: BOX "];
	converters     = ["gameextractor[codes:BOX_LEMBOX]", "dragonUnpacker[types:BOX]"];
}
