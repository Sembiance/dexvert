import {Format} from "../../Format.js";

export class pacmanAdventuresInTimeGameArchive extends Format
{
	name           = "Pacman - Adventures in Time game archive";
	ext            = [".pac"];
	forbidExtMatch = true;
	magic          = ["Pacman - Adventures in Time game data archive", /^geArchive: PAC_CA( |$)/];
	converters     = ["gameextractor[codes:PAC_CA]"];
}
