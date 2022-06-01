import {Format} from "../../Format.js";

export class enableDocument extends Format
{
	name           = "Enable Document";
	ext            = [".wpf"];
	forbidExtMatch = true;
	magic          = ["Enable document"];
	weakMagic      = true;
	converters     = ["strings"];
}
