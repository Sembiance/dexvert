import {xu} from "xu";
import {Format} from "../../Format.js";

export class digitalStudio extends Format
{
	name         = "Digital Studio";
	ext          = [".dst", ".m"];
	magic        = ["Digital Studio (AY)"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
