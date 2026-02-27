import {Format} from "../../Format.js";

export class atgCoreCementGameDataArchive extends Format
{
	name           = "ATG Core Cement game data archive";
	ext            = [".rcf"];
	forbidExtMatch = true;
	magic          = ["ATG Core Cement Format game data archive", /^geArchive: RCF_ATGCORE(_3)?( |$)/, "dragon: RCF "];
	converters     = ["gameextractor[codes:RCF_ATGCORE_3,RCF_ATGCORE]", "dragonUnpacker[types:RCF]"];
}
