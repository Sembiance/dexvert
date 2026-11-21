import {Format} from "../../Format.js";
import {_FFMPEG_CONVERTERS_BUILDER} from "../../program/video/ffmpeg.js";

export class pivotalPSFBank extends Format
{
	name           = "Pivotal PSF Bank Audio";
	ext            = [".wss", ".psf"];
	forbidExtMatch = true;
	magic          = ["Pivotal PSF Bank (psfb)", "vgmstream: psf_segmented", "vgmstream: sch - Pivotal PSF header"];
	metaProvider   = ["ffprobe[libre]"];
	keepFilename   = true;
	converters     = dexState => (["vgmstream[types:psf_segmented]", "vgmstream[types:sch][skipVerify]", _FFMPEG_CONVERTERS_BUILDER({dexState, format : "psfb", outType : "mp3", libre : true})]);
}
