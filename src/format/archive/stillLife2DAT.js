import {Format} from "../../Format.js";

export class stillLife2DAT extends Format
{
	name           = "Still Life 2 DAT Archive";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = [/^geArchive: DAT_GMGB( |$)/];
	converters     = ["gameextractor[codes:DAT_GMGB]"];
}
