import {Format} from "../../Format.js";

export class drpkArchive extends Format
{
	name           = "DRPK Archive";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = [/^geArchive: DAT_DRPK( |$)/];
	converters     = ["gameextractor[codes:DAT_DRPK]"];
}
