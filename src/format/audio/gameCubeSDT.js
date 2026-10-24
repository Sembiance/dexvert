import {Format} from "../../Format.js";

export class gameCubeSDT extends Format
{
	name           = "GameCube SDT Audio";
	ext            = [".sdt"];
	forbidExtMatch = true;
	magic          = ["GameCube SDT (gcsdt)", "vgmstream: sdt"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:gcsdt][outType:mp3]", "vgmstream[types:sdt]"];
}
