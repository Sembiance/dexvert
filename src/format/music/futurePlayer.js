import {Format} from "../../Format.js";

export class futurePlayer extends Format
{
	name         = "FuturePlayer Module";
	ext          = [".fp"];
	magic        = ["FuturePlayer module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
