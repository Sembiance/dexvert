import {Format} from "../../Format.js";

export class follinPlayer extends Format
{
	name         = "Follin Player Module";
	ext          = [".tf"];
	magic        = ["Follin Player II module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
