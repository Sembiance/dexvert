import {Format} from "../../Format.js";

export class datArchive extends Format
{
	name           = "Generic DAT Archive";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = [/^geArchive: DAT_71( |$)/];
	converters     = ["gameextractor[codes:DAT_71]"];
}
