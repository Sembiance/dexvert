import {Format} from "../../Format.js";

export class firstChoice extends Format
{
	name           = "First Choice Document";
	ext            = [".doc", ".pfs"];
	forbidExtMatch = [".doc"];
	weakExt        = true;
	magic          = ["First Choice document", /^fmt\/1282( |$)/];
	converters     = ["fileMerlin[type:PFSFC*]"];
}
