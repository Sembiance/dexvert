import {Format} from "../../Format.js";

export class borlandTurboVisionHelp extends Format
{
	name           = "Borland Turbo Vision Help";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["Borland Turbo Vision Help"];
	converters     = ["strings"];
}
