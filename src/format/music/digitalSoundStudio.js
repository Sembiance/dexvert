import {Format} from "../../Format.js";

export class digitalSoundStudio extends Format
{
	name         = "Digital Sound Studio Module";
	ext          = [".dss"];
	magic        = ["Digital Sound Studio module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
