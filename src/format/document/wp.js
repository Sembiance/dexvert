import {Format} from "../../Format.js";

export class wp extends Format
{
	name           = "WordPerfect document";
	website        = "http://fileformats.archiveteam.org/wiki/WordPerfect";
	ext            = [".wp", ".wpd", ".wp4", ".wp5", ".wp6", ".wp7", ".doc"];
	forbidExtMatch = true;
	magic          = [/^WordPerfect.* [Dd]ocument/, "PerfectOffice document", /^fmt\/(892|1220|1221|1222)( |$)/, /^x-fmt\/(44|393|394)( |$)/];
	weakMagic      = ["WordPerfect document (Amiga)"];	// some documents like OTM.Judas_Priest actually do seem to be Amiga WP documents, but this magic is so loosey goosey (8080*) that I can't trust it at all
	idMeta         = ({macFileType, macFileCreator}) => [".WP5", "sPD3", "WPD1", "WPD2", "WPD3"].includes(macFileType) && macFileCreator==="WPC2";
	converters     = [
		"soffice[format:WordPerfect]", "soffice[format:WordPerfect Graphics]",
		"keyViewPro[outType:pdf]", "fileMerlin", "softwareBridge[format:wp5][noPrevFailedVerify]", "softwareBridge[format:wp][noPrevFailedVerify]", "wordForWord"
	];
}
