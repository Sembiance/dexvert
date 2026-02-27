import {Format} from "../../Format.js";

export class totalAnnihilationHPI extends Format
{
	name           = "Total Annihilation HPI Archive";
	ext            = [".hpi", ".ufo", ".ccx", ".kmp"];
	forbidExtMatch = true;
	magic          = [/^geArchive: (HPI_HAPI_2|HPI_HAPI)( |$)/, "dragon: HPI "];
	converters     = ["gameextractor[codes:HPI_HAPI_2,HPI_HAPI]", "dragonUnpacker[types:HPI]"];
}
