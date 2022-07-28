import {Format} from "../../Format.js";

export class interstateGameData extends Format
{
	name           = "Interstate Series Game Data";
	ext            = [".zfs"];
	forbidExtMatch = true;
	magic          = ["Interstate serie game data archive"];
	weakMagic      = true;
	converters     = ["gameextractor"];
}
