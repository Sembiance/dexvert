import {Format} from "../../Format.js";

export class moneyMatters extends Format
{
	name           = "Money Matters Data";
	ext            = [".mm"];
	forbidExtMatch = true;
	magic          = ["Money Matters"];
	converters     = ["strings"];
}
