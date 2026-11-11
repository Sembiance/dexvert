import {Format} from "../../Format.js";

export class zeroPopulationCountArchive extends Format
{
	name           = "Zero Population Count Archive";
	ext            = [".sce"];
	forbidExtMatch = true;
	magic          = [/^geArchive: SCE_MAP( |$)/];
	converters     = ["gameextractor[codes:SCE_MAP]"];
}
