import {xu} from "xu";
import {Format} from "../../Format.js";

export class html extends Format
{
	name           = "Hypertext Markup Language File";
	website        = "http://fileformats.archiveteam.org/wiki/HTML";
	ext            = [".html", ".htm", ".xhtml", ".xht", ".hhk", ".hhc", ".hts", ".htx", ".shtml", ".phtml"];
	forbidExtMatch = true;
	filename       = [/htm/];
	weakFilename   = true;
	mimeType       = "text/html";
	magic          = [
		// generic HTML
		"HyperText Markup Language with DOCTYPE", "HTML (Hyper Text Markup Language) Datei", "broken XHTML document text", /^Hyper[Tt]ext Markup Language/, /^X?HTML document/, /^text\/html/, /^fmt\/(96|97|98|99|100|102|103|471|1132)( |$)/,

		// app specific HTML
		"IBrowse Hotlist / bookmark (v2)", "Netscape Bookmark", "Internet Explorer bookmark"
	];
	weakMagic      = true;
	trustMagic     = true;
	untouched      = true;
	metaProvider   = ["text"];
	notes          = "I tried some ways I could relax this in order to properly detect HTML files that have no extension, but DOM parsers are really lenient and will parse almost anything as HTML. More than that is too CPU intensive.";
}
