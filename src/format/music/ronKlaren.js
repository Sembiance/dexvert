import {Format} from "../../Format.js";

export class ronKlaren extends Format
{
	name         = "Ron Klaren/CustomMade Module";
	website      = "http://fileformats.archiveteam.org/wiki/Ron_Klaren";
	ext          = [".rk", ".rkb", ".cm"];
	matchPreExt  = true;
	magic        = ["Ron Klaren module", "CustomMade module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
