import {Format} from "../../Format.js";

export class arc0ak extends Format
{
	name           = "ARC 0AK";
	ext            = [".gka"];
	forbidExtMatch = true;
	magic          = [/^geArchive: ARC_0AK( |$)/];
	converters     = ["gameextractor[codes:ARC_0AK]"];
}
