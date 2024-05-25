import {Format} from "../../Format.js";

export class latexAUXFile extends Format
{
	name           = "Latex Auxiliary File";
	ext            = [".aux"];
	forbidExtMatch = true;
	magic          = ["LaTeX auxiliary file", "LaTeX table of contents"];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
