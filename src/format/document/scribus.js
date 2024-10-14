import {Format} from "../../Format.js";

export class scribus extends Format
{
	name           = "Scribus Document";
	website        = "http://fileformats.archiveteam.org/wiki/Scribus";
	ext            = [".sla", ".scd"];
	forbidExtMatch = true;
	magic          = ["Scribus document", "application/vnd.scribus", /^Scribus Document/, /^fmt\/1091( |$)/];
	converters     = ["scribus[outType:pdf]"];
}
