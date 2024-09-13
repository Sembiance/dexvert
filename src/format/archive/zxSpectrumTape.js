import {Format} from "../../Format.js";

export class zxSpectrumTape extends Format
{
	name           = "ZX Spectrum Tape Image";
	ext            = [".tap"];
	forbidExtMatch = true;
	magic          = ["ZX Spectrum Tape image", "Spectrum .TAP data", "Jupiter Ace Tape image", /^fmt\/801( |$)/];
	weakMagic      = true;
	converters     = ["hcdisk"];
}
