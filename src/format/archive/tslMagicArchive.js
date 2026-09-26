import {Format} from "../../Format.js";

export class tslMagicArchive extends Format
{
	name           = "TSL Magic Archive";
	ext            = [".wmw"];
	forbidExtMatch = true;
	magic          = [/^geArchive: TSL_MAGIC( |$)/];
	converters     = ["gameextractor[codes:TSL_MAGIC]"];
}
