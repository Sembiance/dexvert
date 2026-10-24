import {Format} from "../../Format.js";
import {_FFMPEG_CONVERTERS_BUILDER} from "../../program/video/ffmpeg.js";

export class pivotalPSFBank extends Format
{
	name           = "Pivotal PSF Bank Audio";
	ext            = [".wss", ".psf"];
	forbidExtMatch = true;
	magic          = ["Pivotal PSF Bank (psfb)", "vgmstream: psf_segmented"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = dexState => (["vgmstream[types:psf_segmented]", _FFMPEG_CONVERTERS_BUILDER({dexState, format : "psfb", outType : "mp3", libre : true})]);
}
