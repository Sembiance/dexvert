import {Format} from "../../Format.js";

export class mcmd extends Format
{
	name         = "MCMD Module";
	ext          = [".mcmd"];
	magic        = ["MCMD module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
