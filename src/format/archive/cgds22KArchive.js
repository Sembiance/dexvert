import {Format} from "../../Format.js";

export class cgds22KArchive extends Format
{
	name           = "CGDS 22K Archive";
	ext            = [".22k"];
	forbidExtMatch = true;
	magic          = [/^geArchive: 22K_CGDS( |$)/];
	converters     = ["gameextractor[codes:22K_CGDS]"];
}
