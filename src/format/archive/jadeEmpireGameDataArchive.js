import {Format} from "../../Format.js";

export class jadeEmpireGameDataArchive extends Format
{
	name           = "Jade Empire game data archive";
	ext            = [".rim"];
	forbidExtMatch = true;
	magic          = ["Jade Empire game data archive", /^geArchive: RIM_RIMV10( |$)/];
	converters     = ["gameextractor[codes:RIM_RIMV10]"];
}
