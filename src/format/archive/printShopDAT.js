import {Format} from "../../Format.js";

export class printShopDAT extends Format
{
	name             = "The Print Shop DAT";
	website          = "http://fileformats.archiveteam.org/wiki/The_Print_Shop";
	ext              = [".dat"];
	converters       = ["deark[module:printshop]"];
	unsupported      = true;
	notes            = "Deark will extract almost anything ending in .dat and produce garbage PNG files. Since we don't have a better way to identify these files, this can't be safely enabled right now.";
}
