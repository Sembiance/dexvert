import {Format} from "../../Format.js";

export class pixit extends Format
{
	name           = "PIXIT";
	website        = "http://fileformats.archiveteam.org/wiki/PIXIT";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["PIXIT Image (COM)", "16bit COM PIXIT self-display pic", "deark: pixit"];
	converters     = ["deark[module:pixit]"];
}
