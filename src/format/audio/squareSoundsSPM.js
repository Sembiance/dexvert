import {Format} from "../../Format.js";

export class squareSoundsSPM extends Format
{
	name           = "Square Sounds SPM Audio";
	ext            = [".spm"];
	forbidExtMatch = true;
	magic          = ["Square Sounds SPM (spm)", "vgmstream: spm"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:spm][outType:mp3]", "vgmstream[types:spm]"];
}
