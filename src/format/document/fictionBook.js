import {Format} from "../../Format.js";

export class fictionBook extends Format
{
	name           = "FictionBook";
	website        = "https://en.wikipedia.org/wiki/FictionBook";
	ext            = [".fb2"];
	forbidExtMatch = true;
	magic          = ["FictionBook", "application/x-fictionbook+xml"];
	converters     = ["ebook_convert"];
}
