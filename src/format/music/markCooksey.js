import {Format} from "../../Format.js";

export class markCooksey extends Format
{
	name         = "Mark Cooksey Module";
	website      = "http://fileformats.archiveteam.org/wiki/Mark_Cooksey";
	ext          = [".mc", ".mco"];
	magic        = ["Mark Cooksey module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
