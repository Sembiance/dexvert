import {Format} from "../../Format.js";

export class nsaArchive extends Format
{
	name           = "NSA Archive";
	ext            = [".nsa"];
	forbidExtMatch = true;
	magic          = [/^NSA$/, "archive:NScripter.NsaOpener"];
	weakMagic      = true;
	keepFilename   = true;
	converters     = ["GARbro[types:archive:NScripter.NsaOpener]", "unar"];
}
