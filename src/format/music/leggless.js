import {Format} from "../../Format.js";

export class leggless extends Format
{
	name         = "Leggless Music Editor Module";
	ext          = [".lme"];
	magic        = ["Leggless Music Editor module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
