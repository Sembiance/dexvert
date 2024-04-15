import {Format} from "../../Format.js";

export class spectrumPSG extends Format
{
	name         = "Spectrum PSG Chiptune";
	ext          = [".psg"];
	magic        = ["PSG chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "ayEmul[matchType:magic]"];
}
