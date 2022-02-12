import {Format} from "../../Format.js";

export class faustMusicCreator extends Format
{
	name         = "Faust Music Creator";
	ext          = [".sng"];
	magic        = ["Faust Music Creator module"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
