import {Format} from "../../Format.js";

export class clarisWorks extends Format
{
	name           = "ClarisWorks/AppleWorks Document";
	website        = "http://fileformats.archiveteam.org/wiki/ClarisWorks";
	ext            = [".cwk", ".cws"];
	forbidExtMatch = true;
	magic          = [/AppleWorks\/ClarisWorks .+Document/, "Claris Works document", /^fmt\/(736|739|743|744|748|749|845|846|847|849)( |$)/];
	converters     = ["soffice", "mwaw2text"];
	notes          = "Foreign language ClarisWorks files like 差込データ don't convert well at all.";
}
