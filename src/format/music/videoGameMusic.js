import {Format} from "../../Format.js";

export class videoGameMusic extends Format
{
	name         = "Video Game Music";
	ext          = [".vgm"];
	magic        = ["VGM Video Game Music", "Video Game Music format"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
