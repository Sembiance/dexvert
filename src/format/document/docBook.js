import {Format} from "../../Format.js";

export class docBook extends Format
{
	name           = "DocBook";
	website        = "http://fileformats.archiveteam.org/wiki/DocBook";
	ext            = [".dbk", ".xml", ".tmpl"];
	forbidExtMatch = true;
	magic          = ["DocBook Book", "DocBook document", "application/x-docbook+xml", "application/docbook+xml"];
	converters     = ["dblatex"];
}
