import {Format} from "../../Format.js";

export class firstChoice extends Format
{
	name           = "First Choice Document";
	ext            = [".doc", ".pfs"];
	forbidExtMatch = [".doc"];
	weakExt        = true;
	magic          = ["First Choice document", /^fmt\/(1282|1283)( |$)/];
	converters     = ["wordForWord", "fileMerlin[type:PFSFC*]"];
}
