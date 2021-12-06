import {Format} from "../../Format.js";

export class soundInvasion extends Format
{
	name         = "Sound Invasion Module";
	ext          = [".is", ".is20"];
	magic        = ["Sound Invasion Music System module", "Sound Invasion Music System 2.0 module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
