import {Format} from "../../Format.js";

export class pivotalPSFAudio extends Format
{
	name           = "Pivotal PSF Audio";
	ext            = [".psf"];
	forbidExtMatch = true;
	magic          = ["Pivotal PSF (psf)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:psf][outType:mp3]"];
}
