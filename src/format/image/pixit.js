import {Format} from "../../Format.js";

export class pixit extends Format
{
	name           = "PIXIT";
	website        = "http://fileformats.archiveteam.org/wiki/PIXIT";
	ext            = [".com", ".exe"];
	forbidExtMatch = true;
	magic          = [
		"PIXIT Image (COM)", "16bit COM PIXIT self-display pic", "deark: pixit",
		"16bit EXE PIXIT self-display pic"	// not currently supported, see sample/pixit/PIX640.EXX
	];
	converters     = ["deark[module:pixit]"];
}
