import {Format} from "../../Format.js";

export class armobilesWMW extends Format
{
	name           = "Armobiles WMW archive";
	ext            = [".wmw"];
	forbidExtMatch = true;
	magic          = [/^geArchive: WMW_MAGIC( |$)/];
	converters     = ["gameextractor[codes:WMW_MAGIC]"];
}
