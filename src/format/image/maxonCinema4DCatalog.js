import {Format} from "../../Format.js";

export class maxonCinema4DCatalog extends Format
{
	name           = "Maxon Cinema 4D Catalog";
	ext            = [".cat"];
	forbidExtMatch = true;
	magic          = ["Maxon Cinema 4D Catalog"];
	converters     = ["deark[module:jpegscan]"];
}
