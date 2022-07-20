import {Format} from "../../Format.js";

export class kamasOutline extends Format
{
	name           = "KAMAS Outline";
	ext            = [".kam"];
	forbidExtMatch = true;
	magic          = ["KAMAS Outline"];
	converters     = ["strings"];
}
