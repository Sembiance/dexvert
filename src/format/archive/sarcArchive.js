import {Format} from "../../Format.js";

export class sarcArchive extends Format
{
	name           = "SARC Archive";
	ext            = [".arc", ".blz", ".eez"];
	forbidExtMatch = true;
	magic          = [/^geArchive: SARC_SARC( |$)/];
	converters     = ["gameextractor[codes:SARC_SARC]"];
}
