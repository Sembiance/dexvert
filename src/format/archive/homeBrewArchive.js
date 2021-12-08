import {Format} from "../../Format.js";

export class homeBrewArchive extends Format
{
	name        = "HomeBrew Game Data Archive";
	ext         = [".gw1", ".gw2", ".gw3"];
	magic       = ["HomeBrew File Folder game data archive"];
	unsupported = true;
}
