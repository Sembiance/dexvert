import {Format} from "../../Format.js";

export class cWorthyForm extends Format
{
	name           = "C-Worthy Form";
	ext            = [".cwa"];
	forbidExtMatch = true;
	magic          = ["C-Worthy Form"];
	converters     = ["strings"];
}
