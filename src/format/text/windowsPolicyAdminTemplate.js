import {Format} from "../../Format.js";

export class windowsPolicyAdminTemplate extends Format
{
	name         = "Windows Policy Administrative Template";
	magic        = ["Windows Policy Administrative Template"];
	priority     = this.PRIORITY.LOWEST;
	charSet      = "UTF-16";
	untouched    = true;
	metaProvider = ["text"];
}
