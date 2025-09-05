import {Format} from "../../Format.js";

export class photoLinePLD extends Format
{
	name           = "PhotoLine PLD";
	ext            = [".pld"];
	forbidExtMatch = true;
	magic          = ["PhotoLine :pld:"];
	converters     = ["nconvert[format:pld]"];
}
