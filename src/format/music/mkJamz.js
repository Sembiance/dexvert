import {Format} from "../../Format.js";

export class mkJamz extends Format
{
	name         = "MK-Jamz AdLib Module";
	ext          = [".mkj"];
	magic        = ["MK-Jamz Ad Lib module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
