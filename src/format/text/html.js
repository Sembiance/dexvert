import {Format} from "../../Format.js";
import {RUNTIME} from "../../Program.js";

export class html extends Format
{
	name           = "Hypertext Markup Language File";
	website        = "http://fileformats.archiveteam.org/wiki/HTML";
	ext            = [".html", ".htm", ".xhtml", ".xht", ".hhk", ".hhc"];
	forbidExtMatch = true;
	filename       = [/htm/];
	weakFilename   = true;
	mimeType       = "text/html";
	magic          = [/^Hyper[Tt]ext Markup Language/, /^HTML document/, /^fmt\/(96|98|99|100|471)( |$)/];
	weakMagic      = true;
	trustMagic     = true;
	untouched      = () => !RUNTIME.globalFlags?.osHint?.macintoshjp;
	metaProvider   = ["text"];
	converters     = () => [`decodeMacintosh[fileEncoding:iso-8859-1][processor:romanUTF8][region:japan] -> fixMacJPHTML`];	// converters are only used if untouched is false, which only happens if we are japan region
}
