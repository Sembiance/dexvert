import {Format} from "../../Format.js";

export class commandosArchive extends Format
{
	name           = "Commandos Archive";
	ext            = [".pck"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PCK_4( |$)/, "dragon: PCK "];
	converters     = ["gameextractor[codes:PCK_4]", "dragonUnpacker[types:PCK]"];
}
