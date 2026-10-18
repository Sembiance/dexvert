import {Format} from "../../Format.js";

export class elvenLegacyPack extends Format
{
	name           = "Elven Legacy Pack";
	ext            = [".pack"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PACK( |$)/];
	converters     = ["gameextractor[codes:PACK]"];
}
