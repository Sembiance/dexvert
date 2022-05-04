import {Format} from "../../Format.js";

export class clarisWorks extends Format
{
	name           = "ClarisWorks/AppleWorks Document";
	website        = "http://fileformats.archiveteam.org/wiki/ClarisWorks";
	ext            = [".cwk", ".cws"];
	forbidExtMatch = true;
	magic          = [/AppleWorks\/ClarisWorks .+Document/, "Claris Works document", /^fmt\/(743|744|748|749)( |$)/];
	converters     = ["soffice", "mwaw2text"];
}
