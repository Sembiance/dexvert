import {Format} from "../../Format.js";

export class bankGameData extends Format
{
	name           = "Bank Game Data Archive";
	ext            = [".bnk"];
	forbidExtMatch = true;
	magic          = ["Bank game data archive"];
	converters     = ["gameextractor"];
}
