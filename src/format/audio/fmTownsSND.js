import {xu} from "xu";
import {Format} from "../../Format.js";

export class fmTownsSND extends Format
{
	name           = "FM-Towns SND";
	website        = "https://wiki.multimedia.cx/index.php/FM_TOWNS_SND";
	ext            = [".snd"];
	forbidExtMatch = true;
	magic          = ["FM-Towns SND"];
	weakMagic      = true;
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:fmtowns][outType:mp3]", "vibe2wav[renameOut]"];
}
