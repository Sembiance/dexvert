import {Format} from "../../Format.js";

export class moonbaseCommanderGameDataArchive extends Format
{
	name           = "Moonbase Commander game data archive";
	ext            = [".cmp"];
	forbidExtMatch = true;
	magic          = ["Moonbase Commander game data archive", /^geArchive: CMP_MULT( |$)/];
	converters     = ["gameextractor[codes:CMP_MULT]"];
}
