import {Format} from "../../Format.js";

export class professionalPage extends Format
{
	name           = "Professional Page Document";
	forbidExtMatch = true;
	magic          = ["Professional Page document"];
	converters     = ["strings"];
}
