import {Format} from "../../Format.js";

export class escapeVelocityNovaGameDataArchive extends Format
{
	name           = "Escape Velocity Nova game data archive";
	ext            = [".rez", ".off"];
	forbidExtMatch = true;
	magic          = ["Escape Velocity Nova game data archive", /^geArchive: REZ_BRGR( |$)/];
	converters     = ["gameextractor[codes:REZ_BRGR]"];
}
