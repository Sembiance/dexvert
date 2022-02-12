import {Format} from "../../Format.js";

export class ascSoundMaster extends Format
{
	name         = "ASC Sound Master";
	ext          = [".asc"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
