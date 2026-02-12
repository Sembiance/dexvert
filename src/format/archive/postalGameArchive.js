import {Format} from "../../Format.js";

export class postalGameArchive extends Format
{
	name           = "Postal game Archive";
	ext            = [".sak"];
	forbidExtMatch = true;
	magic          = ["Postal game data Archive", /^geArchive: SAK_SAK( |$)/];
	converters     = ["gameextractor[codes:SAK_SAK]"];
}
