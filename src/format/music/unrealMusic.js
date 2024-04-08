import {xu} from "xu";
import {Format} from "../../Format.js";

export class unrealMusic extends Format
{
	name         = "Unreal Music";
	ext          = [".umx"];
	magic        = ["Unreal Music"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123"];
}
