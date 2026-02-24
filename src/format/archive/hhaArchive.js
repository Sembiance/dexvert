import {Format} from "../../Format.js";

export class hhaArchive extends Format
{
	name           = "HHA Archive";
	ext            = [".hha"];
	forbidExtMatch = true;
	magic          = [/^geArchive: HHA( |$)/];
	converters     = ["gameextractor[codes:HHA]"];
}
