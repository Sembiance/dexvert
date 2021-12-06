import {Format} from "../../Format.js";

export class beathovenSynthesizer extends Format
{
	name         = "Beathoven Synthesizer Module";
	ext          = [".bss"];
	magic        = ["Beathoven Synthesizer module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
