import {Format} from "../../Format.js";

export class synArchive extends Format
{
	name           = "SYN Archive";
	ext            = [".syn"];
	forbidExtMatch = true;
	magic          = [/^geArchive: SYN_FNYS( |$)/, "dragon: SYN "];
	converters     = ["gameextractor[codes:SYN_FNYS]", "dragonUnpacker[types:SYN]"];
}
