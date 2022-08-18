import {Format} from "../../Format.js";

export class windowsPolicyAdminTemplateText extends Format
{
	name           = "Windows Policy Administrative Template";
	ext            = [".adm"];
	forbidExtMatch = true;
	magic          = ["Windows Policy Administrative Template"];
	forbiddenMagic = ["Windows Policy Administrative Template (Unicode)"];
	priority       = this.PRIORITY.LOWEST;
	untouched      = true;
	metaProvider   = ["text"];
}
