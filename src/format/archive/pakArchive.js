import {Format} from "../../Format.js";

export class pakArchive extends Format
{
	name           = "PAK Archive";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PAK_37( |$)/];
	converters     = ["gameextractor[codes:PAK_37]"];
}
