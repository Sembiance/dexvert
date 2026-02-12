import {Format} from "../../Format.js";

export class scraplandGameDataArchive extends Format
{
	name           = "Scrapland game data archive";
	ext            = [".packed"];
	forbidExtMatch = true;
	magic          = ["Scrapland game data archive", /^geArchive: PACKED_POZI( |$)/];
	converters     = ["gameextractor[codes:PACKED_POZI]"];
}
