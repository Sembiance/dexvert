import {Format} from "../../Format.js";

export class homeBrewArchive extends Format
{
	name       = "HomeBrew Game Data Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/HomeBrew_File_Folder_Format";
	ext        = [".gw1", ".gw2", ".gw3"];
	magic      = ["HomeBrew File Folder game data archive"];
	converters = ["gamearch"];
}
