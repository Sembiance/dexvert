import {Format} from "../../Format.js";

export class v2m extends Format
{
	name         = "V2 Module";
	ext          = [".v2m"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
