import {Format} from "../../Format.js";

export class harvardTotalProject extends Format
{
	name           = "Harvard Total Project Manager Project";
	ext            = [".prj"];
	forbidExtMatch = true;
	magic          = ["Harvard Total Project Manager Project"];
	converters     = ["strings"];
}
