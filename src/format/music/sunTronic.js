import {Format} from "../../Format.js";

export class sunTronic extends Format
{
	name         = "SUNTronic Module";
	ext          = [".sun"];
	magic        = ["SUNTronic module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
