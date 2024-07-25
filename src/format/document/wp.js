import {Format} from "../../Format.js";

export class wp extends Format
{
	name           = "WordPerfect document";
	website        = "http://fileformats.archiveteam.org/wiki/WordPerfect";
	ext            = [".wp", ".wpd", ".wp4", ".wp5", ".wp6", ".wp7", ".doc"];
	forbidExtMatch = true;
	magic          = [/^WordPerfect.* [Dd]ocument/, "PerfectOffice document", /^fmt\/892( |$)/, /^x-fmt\/(44|393|394)( |$)/];
	converters     = ["soffice[format:WordPerfect]", "soffice[format:WordPerfect Graphics]", "keyViewPro[outType:pdf]", "fileMerlin", "softwareBridge[format:wp5]", "softwareBridge[format:wp]", "wordForWord"];
}
