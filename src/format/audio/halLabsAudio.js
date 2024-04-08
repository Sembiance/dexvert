import {Format} from "../../Format.js";

export class halLabsAudio extends Format
{
	name       = "HAL Laboratory HALPST Audio";
	ext        = [".hps"];
	magic      = ["HAL Laboratory HALPST container audio"];
	converters = ["vgmstream", "zxtune123"];
}
