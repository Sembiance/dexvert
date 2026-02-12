import {Format} from "../../Format.js";

export class mpakGameDataArchive extends Format
{
	name           = "MPAK game data archive";
	ext            = [".mpak"];
	forbidExtMatch = true;
	magic          = ["MPAK game data archive", /^geArchive: MPAK_MPAK( |$)/];
	converters     = ["gameextractor[codes:MPAK_MPAK]"];
}
