import {Format} from "../../Format.js";

export class rfOnlineArchive extends Format
{
	name           = "RF Online Archive";
	ext            = [".rfs"];
	forbidExtMatch = true;
	magic          = [/^geArchive: RFS( |$)/];
	converters     = ["gameextractor[codes:RFS]"];
}
