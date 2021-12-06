import {Format} from "../../Format.js";

export class quadraComposer extends Format
{
	name         = "Quadra Composer";
	ext          = [".emod"];
	magic        = ["Quadra Composer module"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "uade123"];
}
