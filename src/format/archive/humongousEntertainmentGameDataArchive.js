import {Format} from "../../Format.js";

export class humongousEntertainmentGameDataArchive extends Format
{
	name           = "Humongous Entertainment game data archive";
	ext            = [".he2"];
	forbidExtMatch = true;
	magic          = ["Humongous Entertainment game data archive", /^geArchive: HE2_TLKB( |$)/];
	converters     = ["gameextractor[codes:HE2_TLKB]"];
}
