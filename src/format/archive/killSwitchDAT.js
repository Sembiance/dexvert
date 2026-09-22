import {Format} from "../../Format.js";

export class killSwitchDAT extends Format
{
	name           = "Kill Switch DAT Game archive";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = [/^geArchive: DAT_100( |$)/];
	converters     = ["gameextractor[codes:DAT_100]"];
}
