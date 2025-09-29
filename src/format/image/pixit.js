import {Format} from "../../Format.js";

export class pixit extends Format
{
	name           = "PIXIT";
	website        = "http://fileformats.archiveteam.org/wiki/PIXIT";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["PIXIT Image (COM)", "deark: pixit"];
	converters     = ["deark[module:pixit]"];
}
