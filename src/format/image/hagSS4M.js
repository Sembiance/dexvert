import {Format} from "../../Format.js";

export class hagSS4M extends Format
{
	name           = "HAG SS4M Archive";
	ext            = [".ss"];
	forbidExtMatch = true;
	magic          = [/^geViewer: HAG_SS_SS4M( |$)/];
	keepFilename   = true;
	converters     = ["gameextractor[codes:HAG_SS_SS4M]"];
}
