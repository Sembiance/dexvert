import {Format} from "../../Format.js";

export class tempusWord extends Format
{
	name           = "Tempus Word Document";
	ext            = [".twd"];
	forbidExtMatch = true;
	magic          = ["Tempus Word Document"];
	converters     = ["strings"];
}
