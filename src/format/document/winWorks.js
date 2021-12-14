import {Format} from "../../Format.js";

export class winWorks extends Format
{
	name           = "WinWorks Document";
	ext            = [".wpd"];
	forbidExtMatch = true;
	magic          = ["WinWorks text Document"];
	converters     = ["strings"];
}
