import {Format} from "../../Format.js";

export class earAche extends Format
{
	name         = "EarAche Module";
	ext          = [".ea"];
	magic        = ["EarAche module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
