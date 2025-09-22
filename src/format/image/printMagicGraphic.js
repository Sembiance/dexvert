import {Format} from "../../Format.js";

export class printMagicGraphic extends Format
{
	name           = "Print Magic Graphic";
	ext            = [".pmg", ".ico"];
	forbidExtMatch = true;
	magic          = ["Print Magic Graphic"];
	weakMagic      = true;
	converters     = ["wuimg"];
}
