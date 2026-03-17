import {Format} from "../../Format.js";

export class castleStrikeGameArchive extends Format
{
	name           = "Castle Strike Game Archive";
	ext            = [".rda"];
	forbidExtMatch = true;
	magic          = [/^geArchive: RDA_RESOURCEFILE11( |$)/];
	converters     = ["gameextractor[codes:RDA_RESOURCEFILE11]"];
}
