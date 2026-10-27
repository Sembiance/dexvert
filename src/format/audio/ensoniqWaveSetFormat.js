import {Format} from "../../Format.js";

export class ensoniqWaveSetFormat extends Format
{
	name       = "Ensoniq WaveSet Format";
	ext        = [".ecw"];
	magic      = ["Ensoniq WaveSet Format"];
	converters = ["vibe2wav"];
}
