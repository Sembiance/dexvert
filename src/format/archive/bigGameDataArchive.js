import {Format} from "../../Format.js";

export class bigGameDataArchive extends Format
{
	name           = "BIG game data archive";
	ext            = [".big"];
	forbidExtMatch = true;
	magic          = [/^geArchive: BIG_ARCHIVE( |$)/];
	converters     = ["gameextractor[codes:BIG_ARCHIVE]"];
}
