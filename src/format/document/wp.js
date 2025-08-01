import {Format} from "../../Format.js";

export class wp extends Format
{
	name           = "WordPerfect document";
	website        = "http://fileformats.archiveteam.org/wiki/WordPerfect";
	ext            = [".wp", ".wpd", ".wp4", ".wp5", ".wp6", ".wp7", ".doc"];
	forbidExtMatch = true;
	magic          = [/^WordPerfect.* [Dd]ocument/, "PerfectOffice document", /^fmt\/(892|1220|1221)( |$)/, /^x-fmt\/(44|393|394)( |$)/];
	weakMagic      = ["WordPerfect document (Amiga)"];
	idMeta         = ({macFileType, macFileCreator}) => [".WP5", "sPD3", "WPD1", "WPD2", "WPD3"].includes(macFileType) && macFileCreator==="WPC2";
	converters     = [
		"soffice[format:WordPerfect]", "soffice[format:WordPerfect Graphics]",
		"keyViewPro[outType:pdf]", "fileMerlin", "softwareBridge[format:wp5]", "softwareBridge[format:wp]", "wordForWord"
	];
}
