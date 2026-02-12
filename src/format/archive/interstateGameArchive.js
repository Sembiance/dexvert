import {Format} from "../../Format.js";

export class interstateGameArchive extends Format
{
	name           = "Interstate Series Game Archive";
	ext            = [".zfs"];
	forbidExtMatch = true;
	magic          = ["Interstate serie game data archive", "Zork FileSystem game data archive", /^geArchive: ZFS_ZFS( |$)/];
	converters     = ["gameextractor[codes:ZFS_ZFS]"];
}
