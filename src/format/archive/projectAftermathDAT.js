import {Format} from "../../Format.js";

export class projectAftermathDAT extends Format
{
	name           = "Project Aftermath DAT Archive";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = [/^geArchive: DAT_46( |$)/];
	priority       = this.PRIORITY.LOW;
	converters     = ["gameextractor[codes:DAT_46]"];
}
