import {Format} from "../../Format.js";

export class rolandDisk extends Format
{
	name           = "Roland Disk Format";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["Roland Disk Format"];
	converters     = ["vibeExtract"];
}
