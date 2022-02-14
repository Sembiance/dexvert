import {Format} from "../../Format.js";

export class clarionHelp extends Format
{
	name           = "Clarion Help";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["Clarion for DOS Help", "Clarion Developer (v2 and above) help data"];
	trustMagic     = true;
	converters     = ["strings"];
}
