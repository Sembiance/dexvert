import {Format} from "../../Format.js";

export class homeBrewGameArchive extends Format
{
	name           = "HomeBrew Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/HomeBrew_File_Folder_Format";
	ext            = [".gw1", ".gw2", ".gw3"];
	forbidExtMatch = true;
	magic          = ["HomeBrew File Folder game data archive", /^geArchive: GW1_HOME( |$)/];
	converters     = ["gameextractor[codes:GW1_HOME]", "gamearch"];
}
