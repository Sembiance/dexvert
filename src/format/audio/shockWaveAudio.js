import {Format} from "../../Format.js";

const _SHOCKWAVE_AUDIO_MAGIC = ["ShockWave Audio"];
export {_SHOCKWAVE_AUDIO_MAGIC};

export class shockWaveAudio extends Format
{
	name         = "ShockWave Audio";
	website      = "http://fileformats.archiveteam.org/wiki/SWA";
	ext          = [".swa"];
	magic        = _SHOCKWAVE_AUDIO_MAGIC;
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="SwaT" && macFileCreator==="SHCK";
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[outType:mp3]", "vgmstream"];
}
