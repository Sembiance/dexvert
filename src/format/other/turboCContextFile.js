import {Format} from "../../Format.js";

export class turboCContextFile extends Format
{
	name           = "Turbo C Context File";
	ext            = [".dsk"];
	forbidExtMatch = true;
	magic          = ["Turbo C Context"];
	converters     = ["strings"];
}
