import {Format} from "../../Format.js";

export class excelsior extends Format
{
	name           = "Excelsior Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: Excelsior Installer"];
	converters     = ["vibeExtract"];
}
