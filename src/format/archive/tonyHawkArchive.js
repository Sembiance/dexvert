import {Format} from "../../Format.js";

export class tonyHawkArchive extends Format
{
	name           = "Tony Hawk Archive";
	ext            = [".pkr"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PKR_PKR2( |$)/, "dragon: PKR "];
	converters     = ["gameextractor[codes:PKR_PKR2]", "dragonUnpacker[types:PKR]"];
}
