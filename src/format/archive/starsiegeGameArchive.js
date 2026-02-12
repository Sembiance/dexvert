import {Format} from "../../Format.js";

export class starsiegeGameArchive extends Format
{
	name           = "Starsiege Game Archive";
	ext            = [".vol"];
	forbidExtMatch = true;
	magic          = ["Starsiege game data archive", "Starsiege Tribes game data archive", /^geArchive: (VOL_PVOL|VOL_VOL_2)( |$)/];
	converters     = ["gameextractor[codes:VOL_VOL_2,VOL_PVOL]"];
}
