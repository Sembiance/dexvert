import {Format} from "../../Format.js";

export class nintendoDSPAudio extends Format
{
	name           = "Nintendo DSP Audio";
	ext            = [".dsp"];
	forbidExtMatch = true;
	magic          = ["NGC (Nintendo DSP Standard) (ngcdspstd)", "vgmstream: ngc_dsp_aaap", "vgmstream: ngc_dsp_std", "vgmstream: dsp_interleaved"];
	converters     = ["ffmpeg[libre][outType:mp3][format:ngcdspstd]", "vgmstream[types:ngc_dsp_std,ngc_dsp_aaap,dsp_interleaved]"];
}
