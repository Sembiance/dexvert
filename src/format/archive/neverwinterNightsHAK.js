import {Format} from "../../Format.js";

export class neverwinterNightsHAK extends Format
{
	name           = "Neverwinter Nights HAK archive";
	ext            = [".hak"];
	forbidExtMatch = true;
	magic          = [/^geArchive: HAK_HAKV10( |$)/];
	converters     = ["gameextractor[codes:HAK_HAKV10]"];
}
