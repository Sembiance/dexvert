import {Format} from "../../Format.js";

export class renderWareStream extends Format
{
	name           = "RenderWare Stream";
	ext            = [".rws"];
	forbidExtMatch = true;
	magic          = ["RWS (RenderWare Stream) (rws)", "vgmstream: rws"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["vgmstream[types:rws]", "ffmpeg[libre][format:rws][outType:mp3]"];
}
