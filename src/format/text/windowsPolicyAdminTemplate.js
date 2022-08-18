import {Format} from "../../Format.js";

export class windowsPolicyAdminTemplate extends Format
{
	name           = "Windows Policy Administrative Template - Unicode";
	ext            = [".adm"];
	forbidExtMatch = true;
	magic          = ["Windows Policy Administrative Template (Unicode)"];
	priority       = this.PRIORITY.LOWEST;
	charSet        = "UTF-16";
	untouched      = true;
	metaProvider   = ["text"];
}
