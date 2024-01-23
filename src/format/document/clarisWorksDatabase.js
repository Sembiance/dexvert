import {Format} from "../../Format.js";

export class clarisWorksDatabase extends Format
{
	name           = "ClarisWorks Databaset";
	website        = "http://fileformats.archiveteam.org/wiki/ClarisWorks";
	ext            = [".db"];
	forbidExtMatch = true;
	magic          = [/^fmt\/848( |$)/];
	converters     = ["soffice[matchType:magic]", "mwaw2text"];
}
