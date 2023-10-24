import {Format} from "../../Format.js";

export class printShopDAT extends Format
{
	name             = "The Print Shop DAT";
	website          = "http://fileformats.archiveteam.org/wiki/The_Print_Shop";
	ext              = [".dat"];
	converters       = ["deark[module:printshop]"];
	unsupported      = true;
	notes            = "Deark will extract almost anything ending in .dat and produce garbage PNG files. So this can't be safely enabled right now.";
}
