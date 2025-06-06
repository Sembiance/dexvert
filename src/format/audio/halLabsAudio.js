import {Format} from "../../Format.js";

export class halLabsAudio extends Format
{
	name       = "HAL Laboratory HALPST Audio";
	ext        = [".hps"];
	magic      = ["HAL Laboratory HALPST container audio", "HAL Labs (halpst)"];
	converters = ["ffmpeg[libre][format:halpst][outType:mp3]", "vgmstream", "zxtune123"];
}
