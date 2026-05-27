import {Format} from "../../Format.js";

export class zxs extends Format
{
	name         = "ZXS";
	ext          = [".zxs"];
	byteCheck    = [{offset : 0, match : [0x06]}];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
