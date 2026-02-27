import {Format} from "../../Format.js";

export class jp6Archive extends Format
{
	name           = "JP6 Archive";
	ext            = [".jp6"];
	forbidExtMatch = true;
	magic          = [/^geArchive: JP6_JP6( |$)/];
	converters     = ["gameextractor[codes:JP6_JP6]"];
}
