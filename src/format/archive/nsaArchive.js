import {Format} from "../../Format.js";

export class nsaArchive extends Format
{
	name           = "NSA Archive";
	ext            = [".nsa"];
	forbidExtMatch = true;
	magic          = [/^NSA$/];
	weakMagic      = true;
	keepFilename   = true;
	converters     = ["unar"];
}
