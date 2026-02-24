import {Format} from "../../Format.js";

export class neverwinterNightsMOD extends Format
{
	name           = "Neverwinter Nights MOD";
	ext            = [".mod", ".nwm"];
	forbidExtMatch = true;
	magic          = [/^geArchive: NWM_MODV10( |$)/];
	converters     = ["gameextractor[codes:NWM_MODV10]"];
}
