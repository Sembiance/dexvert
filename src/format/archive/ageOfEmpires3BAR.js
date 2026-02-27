import {Format} from "../../Format.js";

export class ageOfEmpires3BAR extends Format
{
	name           = "Age of Empires 3 BAR Archive";
	ext            = [".bar"];
	forbidExtMatch = true;
	magic          = [/^geArchive: BAR_ESPN( |$)/, "dragon: BAR "];
	converters     = ["gameextractor[codes:BAR_ESPN]", "dragonUnpacker[types:BAR]"];
}
