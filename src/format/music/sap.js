import {Format} from "../../Format.js";

export class sap extends Format
{
	name         = "Slight Atari Player";
	website      = "http://fileformats.archiveteam.org/wiki/Slight_Atari_Player";
	ext          = [".sap"];
	magic        = ["Atari 8-bit SAP audio file", "Slight Atari Player music format "];	// trailing space intentional
	metaProvider = ["musicInfo"];
	converters   = ["asapconv", "zxtune123"];
}
