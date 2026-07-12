import {Format} from "../../Format.js";

export class intenium extends Format
{
	name           = "INTENIUM Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: INTENIUM"];
	converters     = ["vibeExtract"];
}
