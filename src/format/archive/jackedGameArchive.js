import {Format} from "../../Format.js";

export class jackedGameArchive extends Format
{
	name           = "Jacked game archive";
	ext            = [".dat", ".old"];
	forbidExtMatch = true;
	magic          = ["Jacked game data archive", /^geArchive: OLD_TORQUE( |$)/];
	converters     = ["gameextractor[codes:OLD_TORQUE]"];
}
