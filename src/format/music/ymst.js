import {Format} from "../../Format.js";

export class ymst extends Format
{
	name         = "YMST Module";
	ext          = [".ymst", ".ym"];
	magic        = ["YM2149 song"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:YM-2149]"];
}
