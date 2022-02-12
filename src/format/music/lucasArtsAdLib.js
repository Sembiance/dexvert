import {Format} from "../../Format.js";

export class lucasArtsAdLib extends Format
{
	name         = "LucasArts AdLib Module";
	ext          = [".laa"];
	magic        = ["LucasArts Ad Lib Audio module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
