import {Format} from "../../Format.js";

export class compressWaveAudio extends Format
{
	name           = "CompressWave audio";
	ext            = [".cwav"];
	forbidExtMatch = true;
	magic          = ["CompressWave audio", "CompressWave CWAV (cmpwave)", "vgmstream: compresswave"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:cmpwave][outType:mp3]", "vgmstream[types:compresswave]"];
}
