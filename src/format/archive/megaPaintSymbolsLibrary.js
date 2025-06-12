import {Format} from "../../Format.js";

export class megaPaintSymbolsLibrary extends Format
{
	name           = "MegaPaint Symbols Library";
	ext            = [".lib"];
	forbidExtMatch = true;
	magic          = ["MegaPaint symbols Library", "deark: megapaint_lib"];
	converters     = ["deark[module:megapaint_lib][extractAll]"];
}
