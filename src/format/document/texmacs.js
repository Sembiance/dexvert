import {Format} from "../../Format.js";

export class texmacs extends Format
{
	name           = "TeXmacs document";
	website        = "https://en.wikipedia.org/wiki/GNU_TeXmacs";
	ext            = [".tm"];
	forbidExtMatch = true;
	magic          = ["GNU TeXmacs document", "text/x-texmacs.doc", /^TeXmacs document/];
	converters     = ["texmacs"];
}
