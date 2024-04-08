import {Format} from "../../Format.js";

export class kefrens extends Format
{
	name         = "Kefrens-Sound Machine Module";
	ext          = [".ksm"];
	magic        = ["Kefrens-Sound Machine song/module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp"];
}
