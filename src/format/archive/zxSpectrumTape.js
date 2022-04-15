import {Format} from "../../Format.js";

export class zxSpectrumTape extends Format
{
	name        = "ZX Spectrum Tape Image";
	ext         = [".tap"];
	magic       = ["ZX Spectrum Tape image", "Spectrum .TAP data"];
	weakMagic   = true;
	unsupported = true;
}
