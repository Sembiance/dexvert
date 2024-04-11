import {Format} from "../../Format.js";

export class zxs extends Format
{
	name         = "ZXS";
	ext          = [".zxs"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "ayEmul"];
}
