import {Format} from "../../Format.js";

export class windowsErrorReport extends Format
{
	name           = "Windows Error Report";
	ext            = [".wer"];
	forbidExtMatch = true;
	magic          = ["Windows Error Report"];
	priority       = this.PRIORITY.LOWEST;
	charSet        = "UTF-16";
	untouched      = true;
	metaProvider   = ["text"];
}
