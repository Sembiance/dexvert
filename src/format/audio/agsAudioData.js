import {Format} from "../../Format.js";

export class agsAudioData extends Format
{
	name           = "Adventure Game Studio Audio Data";
	ext            = [".vox"];
	forbidExtMatch = true;
	magic          = ["AGS audio data"];
	converters     = ["gameextractor[codes:VOX_CLIB,VOX_CLIB_2,VOX_CLIB_3] -> dexvert"];
}
