import {Format} from "../../Format.js";

export class kensAdLib extends Format
{
	name         = "Ken's AdLib";
	ext          = [".ksm"];
	magic        = ["Ken's Adlib Music"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
