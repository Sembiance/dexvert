import {Format} from "../../Format.js";

export class sqDigital extends Format
{
	name           = "SQ Digital Tracker";
	ext            = [".m", ".sqd"];
	forbidExtMatch = [".m"];
	magic          = ["SQ Digital Tracker"];
	metaProvider   = ["musicInfo"];
	converters     = ["zxtune123"];
}
