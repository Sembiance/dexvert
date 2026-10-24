import {Format} from "../../Format.js";

export class capcomASTL extends Format
{
	name           = "Capcom ASTL Audio";
	ext            = [".astl"];
	forbidExtMatch = true;
	magic          = ["Capcom ASTL (Audio Stream) (astl)", "vgmstream: ast_mtf"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:astl][outType:mp3]", "vgmstream[types:ast_mtf]"];
}
