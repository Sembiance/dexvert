import {Format} from "../../Format.js";

export class speedySystem extends Format
{
	name         = "Speedy System Module";
	ext          = [".ss"];
	magic        = ["Speedy System module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
