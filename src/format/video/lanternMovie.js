import {Format} from "../../Format.js";

export class lanternMovie extends Format
{
	name           = "Lantern Movie";
	ext            = [".mov"];
	forbidExtMatch = true;
	magic          = ["Generic IFF FORM file WABM", "Generic RIFF file WABM"];
	converters     = ["na_eofdec"];
}
