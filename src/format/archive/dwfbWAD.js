import {Format} from "../../Format.js";

export class dwfbWAD extends Format
{
	name           = "DWFB WAD";
	ext            = [".wad"];
	forbidExtMatch = true;
	magic          = [/^geArchive: WAD_DWFB( |$)/, "dragon: DWFB "];
	converters     = ["gameextractor[codes:WAD_DWFB]", "dragonUnpacker[types:DWFB]"];
}
