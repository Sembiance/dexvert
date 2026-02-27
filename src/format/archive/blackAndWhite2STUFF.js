import {Format} from "../../Format.js";

export class blackAndWhite2STUFF extends Format
{
	name           = "Black and White 2 STUFF";
	ext            = [".stuff"];
	forbidExtMatch = true;
	magic          = [/^geArchive: STUFF_2( |$)/, "dragon: BW2STUFF "];
	weakMagic      = true;
	converters     = ["gameextractor[codes:STUFF_2]", "dragonUnpacker[types:BW2STUFF]"];
}
