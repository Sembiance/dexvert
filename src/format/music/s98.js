import {Format} from "../../Format.js";

export class s98 extends Format
{
	name         = "PC88/PC9801 Sound Log";
	ext          = [".s98"];
	magic        = ["PC88/PC9801 sound logs rip"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
