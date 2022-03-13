import {Format} from "../../Format.js";

export class microsoftAdvisorHelp extends Format
{
	name           = "Microsoft Advisor Help";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["MS Advisor help file", "Microsoft Advisor Help"];
	unsupported    = true;
}
