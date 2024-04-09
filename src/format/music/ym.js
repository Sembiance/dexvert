import {Format} from "../../Format.js";

export class ym extends Format
{
	name         = "ST-Sound YM Module";
	website      = "http://fileformats.archiveteam.org/wiki/YM";
	ext          = [".ym"];
	magic        = ["ST-Sound YM chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "ym2wav"];
}
