import {Format} from "../../Format.js";

export class uhs extends Format
{
	name           = "Universal Hint System Document";
	website        = "http://fileformats.archiveteam.org/wiki/UHS";
	ext            = [".uhs"];
	forbidExtMatch = true;
	magic          = ["Universal Hint System"];
	converters     = [
		"enforceCRLF -> uhs2html",	// some UHS files don't have proper CRLF line endings, so we enforce them
		"uhs2html"	// this falls back to just uhs2html if enforceCRLF detects that the file already has CRLF line endings
	];
}
