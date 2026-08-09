import {Format} from "../../Format.js";

export class gameCubeSDT extends Format
{
	name           = "GameCube SDT Audio";
	ext            = [".sdt"];
	forbidExtMatch = true;
	magic          = ["GameCube SDT (gcsdt)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:gcsdt][outType:mp3]"];
}
