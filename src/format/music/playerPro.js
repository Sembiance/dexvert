import {Format} from "../../Format.js";

export class playerPro extends Format
{
	name        = "PlayerPro Module";
	ext         = [".mad"];
	magic       = ["PlayerPro module"];
	unsupported = true;	// only 46 unique files on discmaster
}
