import {Format} from "../../Format.js";

export class armobilesBMB extends Format
{
	name           = "Armobiles BMB archive";
	ext            = [".bmb"];
	forbidExtMatch = true;
	magic          = [/^geArchive: BMB_MAGIC( |$)/];
	converters     = ["gameextractor[codes:BMB_MAGIC]"];
}
