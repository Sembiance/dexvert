import {Format} from "../../Format.js";

export class ascaronEntertainmentGameArchive extends Format
{
	name           = "ASCARON Entertainment game archive";
	ext            = [".cpr"];
	forbidExtMatch = true;
	magic          = ["ASCARON Entertainment game data archive", /^geArchive: CPR_ASCARON( |$)/];
	converters     = ["gameextractor[codes:CPR_ASCARON]"];
}
