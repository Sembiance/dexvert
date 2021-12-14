import {Format} from "../../Format.js";

export class macWrite extends Format
{
	name           = "MacWrite Document";
	ext            = [".mcw", ".doc"];
	forbidExtMatch = true;
	magic          = [/^MacWrite [Dd]ocument/];
	converters     = ["soffice"];
}
