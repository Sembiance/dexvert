import {Format} from "../../Format.js";

export class sybaseIAnywhereIndex extends Format
{
	name           = "Sybase iAnywhere Index";
	ext            = [".cdx"];
	forbidExtMatch = true;
	magic          = ["Sybase iAnywhere index files", "xBase compound index"];
	weakMagic      = ["xBase compound index"];
	converters     = ["strings"];
}
