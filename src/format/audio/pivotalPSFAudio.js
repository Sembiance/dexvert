import {Format} from "../../Format.js";

export class pivotalPSFAudio extends Format
{
	name           = "Pivotal PSF Audio";
	ext            = [".psf"];
	forbidExtMatch = true;
	magic          = ["Pivotal PSF (psf)", "vgmstream: psf_single"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:psf][outType:mp3]", "vgmstream[types:psf_single]"];
}
