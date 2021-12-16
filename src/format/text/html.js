import {Format} from "../../Format.js";

export class html extends Format
{
	name           = "Hypertext Markup Language File";
	website        = "http://fileformats.archiveteam.org/wiki/HTML";
	ext            = [".html", ".htm", ".xhtml", ".xht", ".hhk", ".hhc"];
	forbidExtMatch = true;
	mimeType       = "text/html";
	magic          = [/^Hyper[Tt]ext Markup Language/, /^HTML document/];
	weakMagic      = true;
	trustMagic     = true;
	untouched      = true;
	metaProvider   = ["text"];
}
