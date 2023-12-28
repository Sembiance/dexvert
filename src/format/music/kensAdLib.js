import {Format} from "../../Format.js";

export class kensAdLib extends Format
{
	name         = "Ken's AdLib";
	website      = "http://fileformats.archiveteam.org/wiki/Ken's_Adlib_Music";
	ext          = [".ksm"];
	magic        = ["Ken's Adlib Music"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
