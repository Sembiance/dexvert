import {xu} from "xu";
import {Format} from "../../Format.js";

export class fantavision extends Format
{
	name           = "Fantavision Movie";
	ext            = [".mve"];
	forbidExtMatch = true;
	magic          = ["Fantavision Movie"];
	weakMagic      = true;
	converters     = ["fantavsn"];
}
