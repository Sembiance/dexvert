import {Format} from "../../Format.js";

export class iffFormattedText extends Format
{
	name           = "IFF Formatted Text";
	website        = "http://fileformats.archiveteam.org/wiki/FTXT";
	ext            = [".iff", ".ftxt"];
	forbidExtMatch = true;
	magic          = ["IFF data, FTXT formatted text", "IFF-Text document"];
	converters     = ["iff_convert"];
}
