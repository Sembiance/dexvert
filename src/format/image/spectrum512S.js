import {Format} from "../../Format.js";

export class spectrum512S extends Format
{
	name       = "Spectrum 512 Smooshed";
	website    = "http://fileformats.archiveteam.org/wiki/Spectrum_512_formats";
	ext        = [".sps"];
	mimeType   = "image/x-spectrum512-smooshed";
	magic      = ["Spectrum 512 compressed/smooshed bitmap", "deark: spectrum512s (Spectrum 512 Smooshed)"];
	notes      = "Some test files fail to convert correctly: AMBER_F, CANDLE, AI_R_010";
	converters = ["deark[module:spectrum512s]", "recoil2png", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
