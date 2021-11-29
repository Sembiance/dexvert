import {Format} from "../../Format.js";

export class dartDesktop extends Format
{
	name           = "Dart Desktop";
	ext            = [".dsk"];
	forbidExtMatch = true;
	magic          = ["Dart Desktop"];
	converters     = ["strings"];
}
