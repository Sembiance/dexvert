import {Format} from "../../Format.js";

export class volArchive extends Format
{
	name           = "VOL archive";
	ext            = [".vol"];
	forbidExtMatch = true;
	magic          = [/^geArchive: VOL_VOL( |$)/];
	converters     = ["gameextractor[codes:VOL_VOL]"];
}
