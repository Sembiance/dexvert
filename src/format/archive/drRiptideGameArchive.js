import {Format} from "../../Format.js";

export class drRiptideGameArchive extends Format
{
	name           = "Dr. Riptide Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Dr._Riptide)";
	ext            = [".dat"];
	forbidExtMatch = true;
	filename       = [/^(riptide|ccedit)\.dat$/i, /^galvoice\.voc$/i];
	converters     = ["gamearch"];
}
