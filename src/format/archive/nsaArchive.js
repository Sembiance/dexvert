import {Format} from "../../Format.js";

export class nsaArchive extends Format
{
	name           = "BSA Archive";
	ext            = [".nsa"];
	forbidExtMatch = true;
	magic          = [/^NSA$/];
	weakMagic      = true;
	keepFilename   = true;
	converters     = ["unar"];
}
