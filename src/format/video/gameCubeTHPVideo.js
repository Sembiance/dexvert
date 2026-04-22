import {Format} from "../../Format.js";

export class gameCubeTHPVideo extends Format
{
	name           = "GameCube THP Video";
	ext            = [".thp"];
	forbidExtMatch = true;
	magic          = ["THP (thp)", "GameCube THP video"];
	converters     = ["ffmpeg[format:thp][libre]"];
}
