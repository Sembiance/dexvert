import {Format} from "../../Format.js";

export class docBook extends Format
{
	name           = "DocBook";
	website        = "http://fileformats.archiveteam.org/wiki/DocBook";
	ext            = [".dbk", ".xml"];
	forbidExtMatch = true;
	magic          = ["DocBook", "application/x-docbook+xml"];
	converters     = ["dblatex"];
}
