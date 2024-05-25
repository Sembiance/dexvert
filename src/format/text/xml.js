import {Format} from "../../Format.js";

const _XML_MAGIC = ["Extensible Markup Language", "Generic XML", /^XML .*document/, "XML Datei", /^fmt\/101( |$)/];
export {_XML_MAGIC};

export class xml extends Format
{
	name           = "Extensible Markup Language";
	website        = "http://fileformats.archiveteam.org/wiki/XML";
	ext            = [".xml"];
	forbidExtMatch = true;
	mimeType       = "application/xml";
	magic          = _XML_MAGIC;
	untouched      = true;
	metaProvider   = ["text"];
}
