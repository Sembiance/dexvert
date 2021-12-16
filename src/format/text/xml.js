import {Format} from "../../Format.js";

export class xml extends Format
{
	name           = "Extensible Markup Language";
	website        = "http://fileformats.archiveteam.org/wiki/XML";
	ext            = [".xml"];
	forbidExtMatch = true;
	mimeType       = "application/xml";
	magic          = ["Extensible Markup Language", "Generic XML", /^XML .*document/];
	untouched      = true;
	metaProvider   = ["text"];
}
