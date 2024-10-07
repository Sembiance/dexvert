import {Format} from "../../Format.js";

export class vixImagesCatalog extends Format
{
	name           = "ViX images catalog";
	ext            = [".vix"];
	forbidExtMatch = true;
	magic          = ["ViX images catalog"];
	weakMagic      = true;
	converters     = ["foremost"];
}
