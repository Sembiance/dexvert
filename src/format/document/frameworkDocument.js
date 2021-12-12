import {Format} from "../../Format.js";

export class frameworkDocument extends Format
{
	name           = "FrameworkDocument";
	ext            = [".fw2", ".fw3"];
	forbidExtMatch = true;
	magic          = [/^Framework.* document/];
	converters     = ["strings"];
}
