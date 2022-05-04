import {Format} from "../../Format.js";

export class borlandReflexDatabase extends Format
{
	name           = "Borland Reflex Database";
	ext            = [".rxd"];
	forbidExtMatch = true;
	magic          = ["Borland Reflex Database", /^fmt\/393( |$)/];
	converters     = ["strings"];
}
