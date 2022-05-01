import {Format} from "../../Format.js";

export class clarisWorks extends Format
{
	name           = "ClarisWorks Document";
	website        = "http://fileformats.archiveteam.org/wiki/ClarisWorks";
	ext            = [".cwk", ".cws"];
	forbidExtMatch = true;
	magic          = [/AppleWorks\/ClarisWorks .+Document/, "Claris Works document"];
	converters     = ["soffice", "mwaw2text"];
}
