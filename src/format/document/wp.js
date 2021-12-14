import {Format} from "../../Format.js";

export class wp extends Format
{
	name           = "WordPerfect document";
	website        = "http://fileformats.archiveteam.org/wiki/WordPerfect";
	ext            = [".wp", ".wpd", ".wp4", ".wp5", ".wp6", ".wp7", ".doc"];
	forbidExtMatch = true;
	magic          = [/^WordPerfect.* [Dd]ocument/];
	converters     = ["soffice", "fileMerlin"];
}
