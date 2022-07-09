import {Format} from "../../Format.js";

export class beathovenSynthesizer extends Format
{
	name         = "Beathoven Synthesizer Module";
	website      = "http://fileformats.archiveteam.org/wiki/Beathoven_Synthesiser";
	ext          = [".bss"];
	magic        = ["Beathoven Synthesizer module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
