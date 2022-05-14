import {Format} from "../../Format.js";

export class paradoxDatabase extends Format
{
	name           = "Paradox Database Table";
	ext            = [".db"];
	forbidExtMatch = true;
	magic          = [/^fmt\/350( |$)/];
	converters     = ["strings"];
}
