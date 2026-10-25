import {Format} from "../../Format.js";

export class gameCubeTHPVideo extends Format
{
	name           = "GameCube THP Video";
	ext            = [".thp"];
	forbidExtMatch = true;
	magic          = ["THP (thp)", "GameCube THP video", /^Nintendo THP Multimedia/];
	weakMagic      = true;
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[format:thp][libre]"];
}
