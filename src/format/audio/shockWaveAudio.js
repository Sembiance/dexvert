import {Format} from "../../Format.js";

export class shockWaveAudio extends Format
{
	name         = "ShockWave Audio";
	website      = "http://fileformats.archiveteam.org/wiki/SWA";
	ext          = [".swa"];
	magic        = ["ShockWave Audio"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="SwaT" && macFileCreator==="SHCK";
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[outType:mp3]", "vgmstream"];
}
