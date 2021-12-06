import {Format} from "../../Format.js";

export class markCooksey extends Format
{
	name         = "Mark Cooksey Module";
	ext          = [".mc"];
	magic        = ["Mark Cooksey module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
